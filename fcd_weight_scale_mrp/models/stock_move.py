# © 2022 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html

from odoo import models, fields, api


class StockMove(models.Model):
    _inherit = "stock.move"

    fcd_document_line_id = fields.Many2one('fcd.document.line', related="purchase_line_id.fcd_document_line_id")
    fcd_lot_finished = fields.Boolean('fcd.document.line', related="purchase_line_id.fcd_lot_finished")
    weight_log_ids = fields.One2many('fcd.weight.scale.log', 'stock_move_id', string='Weight Log')

    @api.depends("move_line_ids.secondary_uom_qty")
    def _compute_secondary_uom_qty(self):
        for move in self:
            if move.product_id.tracking == "lot":
                move_ids = move.move_line_ids.filtered(lambda x: x.qty_done > 0 and x.secondary_uom_qty > 0 and x.secondary_uom_id.id != False)
                if move_ids:
                    move.secondary_uom_qty = sum(move_ids.mapped('secondary_uom_qty'))
                    move.secondary_uom_id = move_ids[0].secondary_uom_id
            else:
                super(StockMove, move)._compute_secondary_uom_qty()

    @api.depends("secondary_uom_qty", "secondary_uom_id")
    def _compute_product_uom_qty(self):
        for move in self:
            if not move.product_id.tracking == "lot":
                move._compute_helper_target_field_qty()

    def action_complete_stock_move_line(self):
        self.move_line_ids.write({
            "lot_id": self.purchase_line_id.fcd_lot_id.id,
            "qty_done": self.product_uom_qty,
            "secondary_uom_id": self.purchase_line_id.secondary_uom_id.id,
            "secondary_uom_qty": self.purchase_line_id.secondary_uom_qty,
        })

        self.purchase_line_id.fcd_lot_finished = True
