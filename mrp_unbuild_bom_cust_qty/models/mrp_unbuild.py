# © 2021 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (https://www.gnu.org/licenses/lgpl-3.0.html)

from odoo import _, api, models, fields
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError
from odoo.tools import float_round

MESSAGE = (
    "Some of your components are tracked, you have to specify "
    "a manufacturing order in order to retrieve the correct components."
)


class MrpUnbuild(models.Model):
    _inherit = "mrp.unbuild"

    bom_custom_quants = fields.Boolean(
        string="Fill Custom Quants",
        default=True,
        compute="_compute_bom_quants_standard",
        readonly=False,
        store=True,
        help="When selected, you'll be able to add custom quants for unbuild,"
        " and standard ones are not used"
    )
    bom_custom_quants_add_myself = fields.Boolean(
        string="Add Main Product To Custom Quants",
        default=False,
        compute="_compute_bom_custom_quants_add_myself",
        readonly=False,
        store=True,
        help="When selected, main product for this unbuild is also added as"
        " a final component",
    )
    action_add_myself_enabled = fields.Boolean(
        compute="_compute_action_add_myself_enabled",
        help="""
        Technical field that help us enabling adding unbuild product to
        component list
        """,
    )
    bom_quants_ids = fields.One2many(
        comodel_name="mrp.unbuild.bom.quants",
        inverse_name="unbuild_id",
        string="BoM Quants",
        readonly=False,
        states={'done': [('readonly', True)]},
        copy=False,
    )
    bom_quants_total_ids = fields.One2many(
        comodel_name="mrp.unbuild.bom.totals",
        inverse_name="unbuild_id",
        string="BoM Quant Totals",
        copy=False,
    )

    bom_quants_has_totals = fields.Boolean(
        compute="_compute_bom_quants_has_totals",
    )

    bom_line_ids = fields.Many2many(
        comodel_name="mrp.bom.line",
        compute="_compute_bom_line_ids",
    )

    @api.depends("bom_quants_total_ids.bom_line_id")
    def _compute_bom_line_ids(self):
        for record in self:
            bom_line_ids = record.bom_quants_total_ids.bom_line_id
            record.bom_line_ids = [(4, bom_line.id) for bom_line in bom_line_ids]

    def _compute_bom_quants_has_totals(self):
        for record in self:
            if record.bom_quants_total_ids.filtered(lambda x: x.total_qty > 0):
                record.bom_quants_has_totals = True
            else:
                record.bom_quants_has_totals = False

    @api.model
    def create(self, values):
        rec = super().create(values)
        if not rec.mo_id:
            bom_line_myself = (
                rec.bom_custom_quants_add_myself
                and rec._get_bom_line_myself()
                or self.env["mrp.bom.line"]
            )
            for bom_line in (rec.bom_id.bom_line_ids | bom_line_myself):
                # TODO Review values are not saved
                rec.bom_quants_total_ids = [(
                    0,
                    0,
                    {'bom_line_id': bom_line.id}
                )]
        return rec
    
    def _get_bom_line_myself(self):
        bom_line_myself = self.env["mrp.bom.line"].search(
            [("product_id", "=", self.product_id.id)],
            limit=1,
        )
        if not bom_line_myself:
            # Convention: create a reverse instrumental BoM with a product in
            # current selected BoM as main product
            # TODO this product must exist, but if not?
            ref_product_id = self.bom_id.bom_line_ids.filtered(
                lambda x: x.product_id.type == "product"
            )
            if ref_product_id:
                ref_product_id = ref_product_id[0]
            else:
                raise ValidationError(_(
                    "Please select a non-empty BoM for this unbuild and try again"
                ))
            bom_myself = self.env["mrp.bom"].create({
                "sequence": 99,
                "product_tmpl_id": ref_product_id.product_tmpl_id.id,
                "code": _("Auto-generated BoM for inverse product %s unbuild") % self.product_id.display_name,
                "type": "normal",
                "company_id": self.company_id.id,
                "product_qty": 1.0,
                "product_uom_id": ref_product_id.product_uom_id.id,
                "bom_line_ids": [(0, 0, {
                    "product_id": self.product_id.id,
                    "product_qty": 1.0,
                    "product_uom_id": self.product_uom_id.id,
                })],
            })
            bom_line_myself = bom_myself.bom_line_ids
        return bom_line_myself


    @api.depends("mo_id")
    def _compute_bom_quants_standard(self):
        # TODO set again value when mo_id unset?
        for record in self.filtered("mo_id"):
            record.bom_custom_quants = False

    @api.depends("bom_custom_quants")
    def _compute_bom_custom_quants_add_myself(self):
        for record in self.filtered(lambda x: not x.bom_custom_quants):
            record.bom_custom_quants_add_myself = False

    def _compute_action_add_myself_enabled(self):
        for record in self:
            record.action_add_myself_enabled = (
                record.state == "draft"
                and record.bom_custom_quants
                and not record.bom_quants_total_ids.filtered(
                    lambda x: x.bom_line_id.product_id == record.product_id
                )
            )

    def action_validate(self):
        self.ensure_one()
        if self.bom_custom_quants:
            bom_total_errors = []
            for record in self.bom_quants_total_ids:
                if record.total_qty == 0.0 and record.expected_qty > 0.0:
                    bom_total_errors.append(record.bom_line_id.product_id.display_name)
            if bom_total_errors:
                error_totals = ''
                for error in bom_total_errors:
                    error_totals += (("- %s\n") % (error))
                raise ValidationError(_(
                    "Insufficient quantities for\n\n%s\n"
                    "You should register at least one quantity,"
                    " or unset expected quantity for them"
                ) % error_totals)
        return super().action_validate()
    
    def action_unbuild(self):
        """ We need to catch raise behavior when tracked products
            are unbuild without an original manufacturing order and
            go on with another workflow with
            _bypass_tracked_product_without_mo()

            Copied from https://github.com/OCA/manufacture/blob/13.0/mrp_unbuild_tracked_raw_material/models/unbuild.py
        """
        try:
            res = super().action_unbuild()
        except UserError as err:
            # Unbuild is impossible because of MESSAGE
            # original condition of this raise is :
            # any(produce_move.has_tracking != 'none'
            # and not self.mo_id for produce_move in produce_moves)
            if hasattr(err, "name") and err.name == _(MESSAGE):
                return self._bypass_tracked_product_without_mo()
            # Here is the Odoo native raise
            raise err
        return res    
    
    def _bypass_tracked_product_without_mo(self):
        consume_moves = self.env["stock.move"].search(
            [("consume_unbuild_id", "=", self.id)]
        )
        produce_moves = self.env["stock.move"].search([("unbuild_id", "=", self.id)])
        finished_moves = consume_moves.filtered(lambda m: m.product_id == self.product_id)
        consume_moves -= finished_moves

        """
        Fully copied from https://github.com/odoo/odoo/blob/4cc086d330b73514fbc64a7fcf22d8a7a9f1b691/addons/mrp/models/mrp_unbuild.py#L150-L199
        """
        if any(consume_move.has_tracking != 'none' and not self.mo_id for consume_move in consume_moves):
            raise UserError(_('Some of your byproducts are tracked, you have to specify a manufacturing order in order to retrieve the correct byproducts.'))

        for finished_move in finished_moves:
            if finished_move.has_tracking != 'none':
                self.env['stock.move.line'].create({
                    'move_id': finished_move.id,
                    'lot_id': self.lot_id.id,
                    'qty_done': finished_move.product_uom_qty,
                    'product_id': finished_move.product_id.id,
                    'product_uom_id': finished_move.product_uom.id,
                    'location_id': finished_move.location_id.id,
                    'location_dest_id': finished_move.location_dest_id.id,
                })
            else:
                finished_move.quantity_done = finished_move.product_uom_qty

        # TODO: Will fail if user do more than one unbuild with lot on the same MO. Need to check what other unbuild has aready took
        for move in produce_moves | consume_moves:
            if move.has_tracking != 'none':
                """ TODO this should be covered in 
                     * _generate_move_from_bom_line()
                     * and _generate_move_from_bom_quants_total()
                     * OR _generate_produce_moves()
                """
                pass
                # original_move = move in produce_moves and self.mo_id.move_raw_ids or self.mo_id.move_finished_ids
                # original_move = original_move.filtered(lambda m: m.product_id == move.product_id)
                # needed_quantity = move.product_uom_qty
                # moves_lines = original_move.mapped('move_line_ids')
                # if move in produce_moves and self.lot_id:
                #     moves_lines = moves_lines.filtered(lambda ml: self.lot_id in ml.lot_produced_ids)
                # for move_line in moves_lines:
                #     # Iterate over all move_lines until we unbuilded the correct quantity.
                #     taken_quantity = min(needed_quantity, move_line.qty_done)
                #     if taken_quantity:
                #         self.env['stock.move.line'].create({
                #             'move_id': move.id,
                #             'lot_id': move_line.lot_id.id,
                #             'qty_done': taken_quantity,
                #             'product_id': move.product_id.id,
                #             'product_uom_id': move_line.product_uom_id.id,
                #             'location_id': move.location_id.id,
                #             'location_dest_id': move.location_dest_id.id,
                #         })
                #         needed_quantity -= taken_quantity
            else:
                move.quantity_done = float_round(move.product_uom_qty, precision_rounding=move.product_uom.rounding)

        finished_moves._action_done()
        consume_moves._action_done()
        produce_moves._action_done()
        produced_move_line_ids = produce_moves.mapped('move_line_ids').filtered(lambda ml: ml.qty_done > 0)
        consume_moves.mapped('move_line_ids').write({'produce_line_ids': [(6, 0, produced_move_line_ids.ids)]})

        return self.write({'state': 'done'})        
    
    def action_add_myself(self):
        self.ensure_one()
        self.bom_quants_total_ids = [(
            0,
            0,
            {"bom_line_id": self._get_bom_line_myself().id}
        )]
        self.bom_custom_quants_add_myself = True

    def _prepare_move_line_with_lot(self, move, bom_quant_id):
        return {
            "move_id": move.id,
            "lot_id": bom_quant_id.lot_id.id,
            "qty_done": bom_quant_id.custom_qty,
            "product_id": move.product_id.id,
            "product_uom_id": move.product_uom.id,
            "location_id": move.location_id.id,
            "location_dest_id": move.location_dest_id.id,
        }

    def _generate_move_from_bom_line(self, product, product_uom, quantity, bom_line_id=False, byproduct_id=False):
        # Default BoM line quantity is overwritten by custom ones
        bom_quant_ids = False
        if self.bom_custom_quants and bom_line_id:
            bom_line_obj = self.bom_quants_total_ids.filtered(lambda x: x.bom_line_id.id == bom_line_id)
            quantity = bom_line_obj.total_qty
            bom_quant_ids = bom_line_obj.bom_quant_ids

        move = super()._generate_move_from_bom_line(product, product_uom, quantity, bom_line_id=bom_line_id, byproduct_id=byproduct_id)

        if self.bom_custom_quants and bom_line_id and product.tracking != "none" and not all(bom_quant_ids.mapped("has_lot")):
            raise UserError(_("You have to specify a lot for %s") % product.name)

        if bom_quant_ids and product.tracking != "none":
            for bom_quant_id in bom_quant_ids:
                self.env["stock.move.line"].create(
                    self._prepare_move_line_with_lot(move, bom_quant_id)
                )

        return move

    def _generate_produce_moves(self):
        moves = super()._generate_produce_moves()
        # TODO this is actually an Odoo bug: if a product is e.g. a service a
        # move is created, and that has no sense. We opt to remove them, that
        # is possible at this moment, becaause they're in "draft" state
        moves_to_remove = moves.filtered(
            lambda x: x.product_id.type not in ["product", "consu"]
        )
        moves_to_remove.unlink()
        moves -= moves_to_remove
        for record in self.bom_quants_total_ids.filtered(lambda x: x.check_bom_line == False):
            product_id = record.bom_line_id.product_id
            if product_id.type not in ["product", "consu"]:
                continue
            moves += self._generate_move_from_bom_quants_total(record)
        return moves

    def _generate_move_from_bom_quants_total(self, quant_total):
        product = quant_total.bom_line_id.product_id
        product_uom = quant_total.bom_line_id.product_uom_id
        quantity = quant_total.total_qty

        location_id = product.property_stock_production or self.location_id
        location_dest_id = self.location_dest_id or product.with_context(force_company=self.company_id.id).property_stock_production
        warehouse = location_dest_id.get_warehouse()
        move = self.env['stock.move'].create({
            'name': self.name,
            'date': self.create_date,
            'product_id': product.id,
            'product_uom_qty': quantity,
            'product_uom': product_uom.id,
            'procure_method': 'make_to_stock',
            'location_dest_id': location_dest_id.id,
            'location_id': location_id.id,
            'warehouse_id': warehouse.id,
            'unbuild_id': self.id,
            'company_id': self.company_id.id,
        })

        bom_quant_ids = quant_total.bom_quant_ids
        if product.tracking != "none" and not all(bom_quant_ids.mapped("has_lot")):
            raise UserError(_("You have to specify a lot for %s") % product.name)
        if bom_quant_ids and product.tracking != "none":
            for bom_quant_id in bom_quant_ids:
                self.env["stock.move.line"].create(
                    self._prepare_move_line_with_lot(move, bom_quant_id)                
                )

        return move

    def _update_product_qty_from_bom_totals(self):
        if not self.env.user.has_group(
            "mrp_unbuild_bom_cust_qty.group_unbuild_force_exact_qty"
        ):
            return
        for unbuild in self:
            total_qty = unbuild._get_product_qty_from_bom_totals()
            unbuild.product_qty = total_qty if total_qty > 0 else 1

    def _get_product_qty_from_bom_totals(self):
        total_product_qty = sum(
            item.product_uom_id._compute_quantity(
                item.total_qty, self.product_uom_id
            )
            for item in self.bom_quants_total_ids.filtered(
                lambda x: x.product_uom_id.category_id == self.product_uom_id.category_id
            )
        )
        return total_product_qty
