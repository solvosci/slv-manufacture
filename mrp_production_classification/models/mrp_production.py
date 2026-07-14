# Copyright 2026 Solvos Consultoría Informática, S.L. (<https://www.solvos.es>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import _, fields, models
from odoo.exceptions import UserError


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    is_classification_type = fields.Boolean(
        related="picking_type_id.is_classification",
        string="Is Classification",
        store=False,
    )

    classification_planned_qty = fields.Float(
        string="Initial Classification Demand",
        digits="Product Unit",
        copy=False,
        help="Original planned quantity of the bulk component the first "
        "time the classification wizard was opened.",
    )

    def action_open_classification_wizard(self):
        self.ensure_one()

        raw_moves = self.move_raw_ids.filtered(lambda m: m.state != "cancel")
        if len(raw_moves) != 1:
            raise UserError(
                _(
                    "The Classification process expects a single bulk "
                    f"component in the bill of materials. This MO has {len(raw_moves)}."
                )
            )

        if not self.move_finished_ids.filtered(lambda m: m.state != "cancel"):
            raise UserError(
                _(
                    "This MO has no finished product or byproducts defined "
                    "in the bill of materials."
                )
            )

        raw_move = raw_moves[0]
        if not self.classification_planned_qty:
            self.classification_planned_qty = raw_move.product_uom_qty

        wizard = self.env["mrp.classification.wizard"].create(
            {
                "production_id": self.id,
                "raw_move_id": raw_move.id,
                "qty_to_consume": self.classification_planned_qty,
            }
        )
        wizard._prepare_lines()

        return {
            "type": "ir.actions.act_window",
            "name": _("Classification Result"),
            "res_model": "mrp.classification.wizard",
            "res_id": wizard.id,
            "view_mode": "form",
            "target": "new",
        }
