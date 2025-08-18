# © 2025 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See https://www.gnu.org/licenses/lgpl-3.0.html

from odoo import _, models
from odoo.tools.float_utils import float_is_zero


class MrpUnbuild(models.Model):
    _inherit = "mrp.unbuild"


    def action_unbuild(self):
        res = super().action_unbuild()
        for unbuild in self:
            unbuild._reconcile_repair_operations_with_moves()
        return res

    def _reconcile_repair_operations_with_moves(self):
        self.ensure_one()
        if not self.lot_id:
            return

        repairs = self.env["repair.order"].search([
            ("lot_id", "=", self.lot_id.id),
            ("state", "=", "done"),
        ], order='id')
        if not repairs:
            return

        for repair in repairs:
            for op in repair.operations:
                if op.type not in ("remove", "add"):
                    continue
                if op.product_uom_qty <= 0:
                    continue

                if op.type == "remove":
                    self._apply_remove_operation(self.produce_line_ids.move_line_ids, op)
                else:
                    self._apply_add_operation(self.produce_line_ids.move_line_ids, op)

    def _apply_remove_operation(self, move_lines, op):
        rounding = op.product_uom.rounding

        candidates = move_lines.filtered(lambda ml:
            ml.product_id == op.product_id
            and not float_is_zero(ml.qty_done, precision_rounding=rounding)
            and ((op.lot_id and ml.lot_id == op.lot_id) or (not op.lot_id and not ml.lot_id))
        )
        if not candidates:
            return

        qty_to_remove = op.product_uom_qty
        for ml in candidates:
            if float_is_zero(qty_to_remove, precision_rounding=rounding):
                break
            reducible = min(ml.qty_done, qty_to_remove)
            new_qty = ml.qty_done - reducible

            ml.qty_done = new_qty

            qty_to_remove -= reducible

    def _apply_add_operation(self, move_lines, op):
        existing = move_lines.filtered(lambda ml:
            ml.product_id == op.product_id and (
                (op.lot_id and ml.lot_id == op.lot_id) or (not op.lot_id and not ml.lot_id)
            )
        )
        if existing:
            target_ml = existing[0]
            target_ml.qty_done = target_ml.qty_done + op.product_uom_qty
            return

        production_location = self.env["stock.location"].search(
            [("usage", "=", "production"),
            ("company_id", "in", [False, self.env.company.id])], limit=1)
        move = self.env["stock.move"].create({
            "name": self.name,
            "unbuild_id": self.id,
            "product_id": op.product_id.id,
            "product_uom_qty": op.product_uom_qty,
            "product_uom": op.product_uom.id,
            "state": "done",
            "location_id": production_location.id,
            "location_dest_id": self.location_dest_id.id,
            "company_id": self.company_id.id,
        })

        vals_ml = {
            "move_id": move.id,
            "qty_done": op.product_uom_qty,
            "product_id": op.product_id.id,
            "product_uom_id": op.product_uom.id,
            "location_id": move.location_id.id,
            "location_dest_id": move.location_dest_id.id,
        }
        if op.lot_id:
            vals_ml["lot_id"] = op.lot_id.id

        self.env["stock.move.line"].create(vals_ml)
