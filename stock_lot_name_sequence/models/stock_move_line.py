# Copyright 2026 Solvos Consultoría Informática, S.L. (<https://www.solvos.es>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    def action_suggest_lot_name_move(self):
        self.ensure_one()
        self._suggest_lot_name()
        return self.move_id.action_show_details()

    def action_suggest_lot_name_picking(self):
        self.ensure_one()
        self._suggest_lot_name()

    def _suggest_lot_name(self):
        self.ensure_one()
        if not self.product_id:
            return
        siblings = (self.picking_id.move_line_ids if self.picking_id else self.move_id.move_line_ids) - self
        sibling_names = siblings.filtered("lot_name").mapped("lot_name")
        self.lot_name = self.env["stock.lot"]._suggest_names(
            [self.product_id], self.company_id, extra_names=sibling_names
        )[0]
