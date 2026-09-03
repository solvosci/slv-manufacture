# Copyright 2026 Solvos Consultoría Informática, S.L. (<https://www.solvos.es>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import fields, models
from odoo.exceptions import UserError


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    is_classification_type = fields.Boolean(
        related="picking_type_id.is_classification",
        string="Is Classification",
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
                self.env._(
                    "The Classification process expects a single bulk "
                    "component in the bill of materials. This MO has %s.",
                    len(raw_moves),
                )
            )

        if not self.move_finished_ids.filtered(lambda m: m.state != "cancel"):
            raise UserError(
                self.env._(
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
            "name": self.env._("Classification Result"),
            "res_model": "mrp.classification.wizard",
            "res_id": wizard.id,
            "view_mode": "form",
            "target": "new",
        }

    def button_mark_done(self):
        classification_orders = self.filtered(
            lambda p: p.picking_type_id.is_classification
        )
        if self - classification_orders:
            return super().button_mark_done()

        # Block the native consumption warning wizard from
        # popping up when marking a classification order as done.
        return super(
            MrpProduction, self.with_context(skip_consumption=True)
        ).button_mark_done()
