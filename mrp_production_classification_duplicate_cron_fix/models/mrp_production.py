# Copyright 2026 Solvos Consultoría Informática, S.L. (<https://www.solvos.es>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models
from odoo.tools.float_utils import float_compare


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    classification_duplicate_lines_fixed = fields.Boolean(
        copy=False,
    )

    def _fix_classification_duplicate_lot_lines(self):
        self.ensure_one()
        precision = self.env["decimal.precision"].precision_get("Product Unit")
        lines = self.move_finished_ids.filtered(
            lambda m: m.state == "done"
        ).move_line_ids

        groups = {}
        for line in lines:
            if not line.lot_id:
                continue
            key = (line.product_id, line.lot_id)
            groups.setdefault(key, self.env["stock.move.line"])
            groups[key] |= line

        for group_lines in groups.values():
            if len(group_lines) != 2:
                continue
            placeholder = group_lines.filtered(
                lambda l: float_compare(l.quantity, 1.0, precision_digits=precision)
                == 0
            )
            if len(placeholder) != 1:
                continue
            other = group_lines - placeholder
            other.quantity += placeholder.quantity
            placeholder.quantity = 0.0

    @api.model
    def _cron_fix_classification_duplicate_lot_lines(self):
        orders = self.search(
            [
                ("state", "=", "done"),
                ("is_classification_type", "=", True),
                ("classification_duplicate_lines_fixed", "=", False),
            ]
        )
        for order in orders:
            order._fix_classification_duplicate_lot_lines()
        orders.write({"classification_duplicate_lines_fixed": True})
