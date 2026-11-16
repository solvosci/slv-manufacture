from odoo import _, api, fields, models


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    custom_pre_prod_location_id = fields.Many2one(
        comodel_name='stock.location',
        string='Pre-Prod-Check location',
        copy=False,
        help='First custom location of the order: the components are sent '
        'here from the main stock.',
    )
    custom_in_process_location_id = fields.Many2one(
        comodel_name='stock.location',
        string='In-Process location',
        copy=False,
        help='Second custom location of the order: the components wait here '
        'while they are physically manufactured.',
    )
    custom_location_src_id = fields.Many2one(
        comodel_name='stock.location',
        string='Post-Prod-Check location (source)',
        copy=False,
        help=(
            'Last custom location of the order and source location of its components. '
            'Generated automatically on creation when the operation type has '
            '"Custom source location per manufacturing order" enabled.'
        ),
    )
    custom_route_id = fields.Many2one(
        comodel_name="stock.location.route",
        string="Custom route for this MO",
        copy=False,
        help="When a MO has custom locations, a custom route is required as well.",
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
        """Return True if the current operation type requires custom locations."""
        self.ensure_one()
        return bool(self.picking_type_id.mrp_custom_src_location)

    # -------------------------------------------------------------------------
    # Custom locations
    # -------------------------------------------------------------------------

    def _get_custom_location_specs(self):
        """Custom locations as (field name, name prefix), in the order the
        components go through them."""
        return [
            ('custom_pre_prod_location_id', 'Pre-Prod-Check'),
            ('custom_in_process_location_id', 'In-Process'),
            ('custom_location_src_id', 'Post-Prod-Check'),
        ]

    def _get_custom_location_name(self, prefix):
        self.ensure_one()
        order_name = (self.name or _('New manufacturing order')).replace('/', '-')
        return '%s-%s' % (prefix, order_name)

    def _get_custom_locations(self):
        self.ensure_one()
        locations = self.env['stock.location']
        for field_name, _prefix in self._get_custom_location_specs():
            locations |= self[field_name]
        return locations

    def _create_custom_locations(self):
        """Create the custom locations under pbm_loc_id and return the values
        to write on the order, or an empty dict if not applicable."""
        self.ensure_one()
        pbm_location = self._get_warehouse_pbm_location()
        if not pbm_location:
            return {}
        vals = {}
        for field_name, prefix in self._get_custom_location_specs():
            name = self._get_custom_location_name(prefix)
            vals[field_name] = self.env['stock.location'].sudo().create({
                'name': name,
                'location_id': pbm_location.id,
                'usage': 'internal',
                'active': True,
                'company_id': self.company_id.id,
                'comment': _(
                    'Custom location %(location)s for manufacturing order %(order)s'
                ) % {'location': name, 'order': self.name},
            }).id
        vals['location_src_id'] = vals['custom_location_src_id']
        return vals

    def _update_draft_raw_moves_location(self):
        self.ensure_one()
        self.move_raw_ids.filtered(lambda m: m.state == 'draft').write({
            'location_id': self.location_src_id.id,
        })

    def _set_custom_locations(self):
        for production in self:
            vals = production._create_custom_locations()
            if vals:
                production.write(vals)
                production._update_draft_raw_moves_location()

    def _archive_custom_locations(self):
        """Archive the custom locations of the orders that carry no stock."""
        for production in self:
            locations = production._get_custom_locations()
            with_stock = self.env['stock.quant'].sudo().search([
                ('location_id', 'in', locations.ids),
                ('quantity', '!=', 0),
            ]).location_id
            (locations - with_stock).sudo().write({'active': False})

    def _unset_custom_locations(self):
        """Archive the custom locations and restore the default source location."""
        for production in self:
            production._archive_custom_locations()
            picking_type = production.picking_type_id
            default_src = (
                picking_type.default_location_src_id
                or picking_type.warehouse_id.lot_stock_id
            )
            vals = {field_name: False for field_name, _prefix in production._get_custom_location_specs()}
            if default_src:
                vals['location_src_id'] = default_src.id
            production.write(vals)
            production._update_draft_raw_moves_location()

    # -------------------------------------------------------------------------
    # Custom route
    # -------------------------------------------------------------------------

    def _get_first_step_procure_method(self):
        """Supply method of the first step (Stock -> Pre-Prod-Check).

        'mts_else_mto' takes from stock when it is available and, if not, triggers
        the supply rule of the product (manufacture, buy...) in the main stock.
        """
        self.ensure_one()
        return 'mts_else_mto'

    def _get_custom_route_steps(self):
        self.ensure_one()
        warehouse = self.picking_type_id.warehouse_id
        pre_prod = self.custom_pre_prod_location_id
        in_process = self.custom_in_process_location_id
        post_prod = self.custom_location_src_id
        return [
            (warehouse.lot_stock_id, pre_prod, warehouse.pbm_type_id, self._get_first_step_procure_method()),
            (pre_prod, in_process, warehouse.int_type_id, 'make_to_order'),
            (in_process, post_prod, warehouse.int_type_id, 'make_to_order'),
            (post_prod, warehouse._get_production_location(), self.picking_type_id, 'make_to_order'),
        ]

    def _create_custom_route(self):
        """Create a dedicated route for this order, with one pull rule per step."""
        self.ensure_one()
        warehouse = self.picking_type_id.warehouse_id
        route = self.env['stock.location.route'].sudo().create({
            'name': "%s: Select components and then produce (%s)" % (warehouse.name, self.name),
            'sequence': 1000,
            'company_id': self.company_id.id,
            'warehouse_selectable': True,
            'warehouse_ids': [(4, warehouse.id)],
        })
        steps = self._get_custom_route_steps()
        for sequence, (src, dest, picking_type, procure_method) in enumerate(steps, start=1):
            self.env['stock.rule'].sudo().create({
                'name': '%s: %s → %s' % (warehouse.code, src.name, dest.name),
                'route_id': route.id,
                'action': 'pull',
                'procure_method': procure_method,
                'location_src_id': src.id,
                'location_id': dest.id,
                'picking_type_id': picking_type.id,
                'warehouse_id': warehouse.id,
                'group_propagation_option': 'propagate',
                'company_id': self.company_id.id,
                'sequence': sequence * 10,
            })
        self.custom_route_id = route

    def _archive_custom_route(self):
        routes = self.custom_route_id.sudo()
        routes.rule_ids.write({'active': False})
        routes.write({'active': False})

    def _archive_custom_locations(self):
        """Archive the custom locations of the orders that carry no stock."""
        for production in self:
            locations = production._get_custom_locations()
            with_stock = self.env['stock.quant'].sudo().search([
                ('location_id', 'in', locations.ids),
                ('quantity', '!=', 0),
            ]).location_id
            (locations - with_stock).sudo().write({'active': False})

    # -------------------------------------------------------------------------
    # ORM overrides
    # -------------------------------------------------------------------------

    @api.model_create_multi
    def create(self, vals_list):
        # Call super first so the sequence name (e.g. WH/MO/00001) is already set
        # before we use it as the location name.
        productions = super().create(vals_list)
        productions.filtered(
            lambda p: p._picking_type_uses_custom_location()
        )._set_custom_locations()
        return productions

    def write(self, vals):
        if 'picking_type_id' not in vals:
            return super().write(vals)
        # Capture the state before the operation type changes (draft orders only)
        pre_state = {
            production.id: (
                production._picking_type_uses_custom_location(),
                production._get_warehouse_pbm_location(),
            )
            for production in self.filtered(lambda p: p.state == 'draft')
        }
        result = super().write(vals)
        for production in self.filtered(lambda p: p.id in pre_state):
            had_custom, old_pbm = pre_state[production.id]
            uses_custom = production._picking_type_uses_custom_location()
            new_pbm = production._get_warehouse_pbm_location()
            if had_custom and not uses_custom:
                production._unset_custom_locations()
            elif uses_custom and not had_custom:
                production._set_custom_locations()
            elif uses_custom and new_pbm and new_pbm != old_pbm:
                # Warehouse changed: the locations must hang from the new one
                production._unset_custom_locations()
                production._set_custom_locations()
        return result

    def action_confirm(self):
        for production in self.filtered(
            lambda p: p.custom_location_src_id and not p.custom_route_id
        ):
            production._create_custom_route()
        return super().action_confirm()

    def _action_cancel(self):
        res = super()._action_cancel()
        self._archive_custom_route()
        self._archive_custom_locations()
        return res

    def button_mark_done(self):
        action = super().button_mark_done()
        # The action is a wizard when the order is not done yet
        done = self.filtered(lambda p: p.state == 'done')
        done._archive_custom_route()
        done._archive_custom_locations()
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
                        'On save, dedicated Pre-Production locations will be created '
                        'automatically for this order under warehouse "%s".'
                    ) % self.picking_type_id.warehouse_id.name,
                }
            }

        if had_custom and not now_uses_custom:
            return {
                'warning': {
                    'title': _('Custom source location'),
                    'message': _(
                        'On save, the custom locations of this order will be archived '
                        '(provided they hold no stock) and the source location restored.'
                    ),
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
                            'The warehouse has changed. On save, the current custom '
                            'locations will be archived and new ones will be created '
                            'under "%s".'
                        ) % new_pbm.display_name,
                    }
                }