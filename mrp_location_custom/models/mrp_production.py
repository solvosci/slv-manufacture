from odoo import api, fields, models, _


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    custom_location_src_id = fields.Many2one(
        comodel_name='stock.location',
        string='Custom source location',
        copy=False,
        help=(
            'Pre-Production location created specifically for this manufacturing order. '
            'Generated automatically on creation when the operation type has '
            '"Custom source location per manufacturing order" enabled.'
        ),
    )

    custom_route_id = fields.Many2one(
        comodel_name="stock.location.route",
        string="Custom route for this MO",
        copy=False,
        help="""
            When a MO has a custom Pre-Production location, a custom route is required as well
        """,
    )

    # -------------------------------------------------------------------------
    # Helpers
    # -------------------------------------------------------------------------

    def _get_warehouse_pbm_location(self):
        """Return the Pre-Production location (pbm_loc_id) of the warehouse
        linked to this order's operation type, or False if not applicable."""
        self.ensure_one()
        warehouse = self.picking_type_id.warehouse_id
        if warehouse and warehouse.pbm_loc_id:
            return warehouse.pbm_loc_id
        return False

    def _picking_type_uses_custom_location(self):
        """Return True if the current operation type requires a custom source location."""
        self.ensure_one()
        return bool(self.picking_type_id.mrp_custom_src_location)

    def _create_custom_src_location(self):
        """Create a child location under pbm_loc_id and return it."""
        self.ensure_one()
        pbm_location = self._get_warehouse_pbm_location()
        if not pbm_location:
            return False

        location_name = (self.name or _('New manufacturing order')).replace('/', '-')
        return self.env['stock.location'].create({
            'name': location_name,
            'location_id': pbm_location.id,
            'usage': 'internal',
            'active': True,
            'company_id': self.company_id.id,
            'comment': _(
                'Custom Pre-Production location for manufacturing order %s'
            ) % location_name,
        })

    def _archive_custom_src_location(self):
        """Archive the custom location if it exists and carries no stock."""
        self.ensure_one()
        loc = self.custom_location_src_id
        if not loc:
            return
        has_stock = self.env['stock.quant'].search_count([
            ('location_id', '=', loc.id),
            ('quantity', '!=', 0),
        ])
        if not has_stock:
            loc.write({'active': False})

    def _create_custom_route(self):
        """Create a dedicated 2-step route (Pick + Make) for this manufacturing
        order, using the per-order custom location as the intermediate point.
        The route is created with the lowest possible sequence so existing
        warehouse rules take precedence in any other context.

        Stores the created route in a new field  custom_route_id  (Many2one to
        stock.route) that must be declared alongside this method.
        """
        self.ensure_one()
        custom_loc = self.custom_location_src_id
        warehouse  = self.picking_type_id.warehouse_id

        # Picking types involved
        # pbm_type  : 'Pick Components' operation type of the warehouse
        # manu_type : 'Manufacturing'   operation type (self.picking_type_id)
        pbm_type  = warehouse.pbm_type_id
        manu_type = self.picking_type_id

        route = self.env['stock.location.route'].create({
            'name': "%s: Select components and then produce (%s)" % (warehouse.name, self.name),
            'sequence': 1000,          # highest sequence = lowest priority
            'company_id': self.company_id.id,
            'warehouse_selectable': True,
            'warehouse_ids': [(4, warehouse.id)],
        })

        # Rule 1 — Pick Components: Stock → custom_loc
        # Mirrors pbm_mto_pull_id but with exact location_id = custom_loc.
        self.env['stock.rule'].create({
            'name': '%s: %s → %s' % (warehouse.code, warehouse.lot_stock_id.name, custom_loc.name),
            'route_id': route.id,
            'action': 'pull',
            'procure_method': 'make_to_stock',   # take from stock
            'location_id': custom_loc.id,         # where components are needed
            'location_src_id': warehouse.lot_stock_id.id,  # from stock
            'picking_type_id': pbm_type.id,
            'warehouse_id': warehouse.id,
            'group_propagation_option': 'propagate',
            'company_id': self.company_id.id,
            'sequence': 10,
        })

        # Rule 2 — Manufacture: custom_loc → production location
        # Mirrors manufacture_pull_id but with location_src_id = custom_loc.
        production_location_id = warehouse._get_production_location()
        self.env['stock.rule'].create({
            'name': '%s: %s → %s' % (warehouse.code, custom_loc.name, production_location_id.name),
            'route_id': route.id,
            'action': 'pull',
            'procure_method': 'make_to_order',
            'location_id': production_location_id.id,
            'location_src_id': custom_loc.id,
            'picking_type_id': manu_type.id,
            'warehouse_id': warehouse.id,
            'group_propagation_option': 'propagate',
            'company_id': self.company_id.id,
            'sequence': 20,
        })

        self.custom_route_id = route

    def _archive_custom_route(self):
        route_ids = self.custom_route_id
        route_ids.rule_ids.write({'active': False})
        route_ids.write({'active': False})        

    # -------------------------------------------------------------------------
    # ORM overrides
    # -------------------------------------------------------------------------

    @api.model
    def create(self, vals):
        # Call super first so the sequence name (e.g. WH/MO/00001) is already set
        # before we use it as the location name.
        production = super().create(vals)

        if production._picking_type_uses_custom_location():
            custom_loc = production._create_custom_src_location()
            if custom_loc:
                production.write({
                    'custom_location_src_id': custom_loc.id,
                    'location_src_id': custom_loc.id,
                })
                # TODO check if moves are still at 'draft' state
                production.move_raw_ids.write({'location_id': custom_loc.id})

        return production

    def write(self, vals):
        # Capture pre-write state for draft orders when the operation type changes.
        picking_type_changed = 'picking_type_id' in vals
        pre_state = {}
        if picking_type_changed:
            for production in self.filtered(lambda p: p.state == 'draft'):
                pre_state[production.id] = {
                    'had_custom': production._picking_type_uses_custom_location(),
                    'custom_location_src_id': production.custom_location_src_id.id,
                    'pbm_loc_id': (
                        production._get_warehouse_pbm_location().id
                        if production._get_warehouse_pbm_location() else False
                    ),
                }

        result = super().write(vals)

        if not (picking_type_changed and pre_state):
            return result

        affected = self.filtered(lambda p: p.id in pre_state)

        # --- Case 1: now requires custom location, previously did not -----------
        to_create = affected.filtered(
            lambda p: not pre_state[p.id]['had_custom']
            and p._picking_type_uses_custom_location()
        )
        for production in to_create:
            custom_loc = production._create_custom_src_location()
            if custom_loc:
                production.write({
                    'custom_location_src_id': custom_loc.id,
                    'location_src_id': custom_loc.id,
                })
                # TODO make the same at other cases
                # TODO check if moves are still at 'draft' state
                production.move_raw_ids.write({'location_id': custom_loc.id})


        # --- Case 2: no longer requires custom location -------------------------
        to_remove = affected.filtered(
            lambda p: pre_state[p.id]['had_custom']
            and not p._picking_type_uses_custom_location()
        )
        for production in to_remove:
            production._archive_custom_src_location()
            default_src = (
                production.picking_type_id.default_location_src_id
                or production.picking_type_id.warehouse_id.lot_stock_id
            )
            production.write({
                'custom_location_src_id': False,
                'location_src_id': default_src.id if default_src else False,
            })

        # --- Case 3: both types use custom location but warehouse changed -------
        to_relocate = affected.filtered(
            lambda p: pre_state[p.id]['had_custom']
            and p._picking_type_uses_custom_location()
            and p._get_warehouse_pbm_location()
            and pre_state[p.id]['pbm_loc_id'] != p._get_warehouse_pbm_location().id
        )
        for production in to_relocate:
            old_loc = self.env['stock.location'].browse(
                pre_state[production.id]['custom_location_src_id']
            )
            has_stock = self.env['stock.quant'].search_count([
                ('location_id', '=', old_loc.id),
                ('quantity', '!=', 0),
            ])
            if not has_stock:
                old_loc.write({'active': False})
            custom_loc = production._create_custom_src_location()
            if custom_loc:
                production.write({
                    'custom_location_src_id': custom_loc.id,
                    'location_src_id': custom_loc.id,
                })

        return result

    def action_confirm(self):
        for mrp in self.filtered(lambda x: x.custom_location_src_id):
            mrp._create_custom_route()
        return super().action_confirm()

    def _action_cancel(self):
        res = super()._action_cancel()
        self._archive_custom_route()
        # TODO custom location archive management
        return res

    def button_mark_done(self):
        action = super().button_mark_done()
        self._archive_custom_route()
        # TODO custom location archive management
        return action

    # -------------------------------------------------------------------------
    # Onchange for UX
    # -------------------------------------------------------------------------

    @api.onchange('picking_type_id')
    def _onchange_picking_type_custom_location(self):
        if self.state != 'draft':
            return

        now_uses_custom = self._picking_type_uses_custom_location()
        had_custom = bool(self.custom_location_src_id)

        if not had_custom and now_uses_custom:
            return {
                'warning': {
                    'title': _('Custom source location'),
                    'message': _(
                        'On save, a dedicated Pre-Production location will be created '
                        'automatically for this order under warehouse "%s".'
                    ) % self.picking_type_id.warehouse_id.name,
                }
            }

        if had_custom and not now_uses_custom:
            return {
                'warning': {
                    'title': _('Custom source location'),
                    'message': _(
                        'On save, the custom source location "%s" will be archived '
                        '(provided it holds no stock) and the field will be cleared.'
                    ) % self.custom_location_src_id.display_name,
                }
            }

        if had_custom and now_uses_custom:
            old_pbm = self.custom_location_src_id.location_id
            new_pbm = self._get_warehouse_pbm_location()
            if old_pbm and new_pbm and old_pbm.id != new_pbm.id:
                return {
                    'warning': {
                        'title': _('Custom source location'),
                        'message': _(
                            'The warehouse has changed. On save, the current custom source '
                            'location will be archived and a new one will be created '
                            'under "%s".'
                        ) % new_pbm.display_name,
                    }
                }
