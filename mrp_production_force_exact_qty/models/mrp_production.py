# © 2023 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (https://www.gnu.org/licenses/lgpl-3.0.html)

from odoo import _, models
from odoo.exceptions import ValidationError
from odoo.tools import float_is_zero


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    def button_mark_done(self):
        if not self.env.context.get("mrp_force_exact_skip", False):
            for mrp in self:
                mrp._check_button_mark_done()
        return super().button_mark_done()

    def _check_button_mark_done(self):
        # We'll only check quantities if every consumed and produced move
        #  belongs to the same UoM cateogory. Other operation should be
        #  inconsistent
        # TODO float_compare
        consumed_moves = self.move_raw_ids.filtered(
            lambda x: x.quantity > 0.0
        )
        produced_moves = self.move_finished_ids.filtered(
            lambda x: x.quantity > 0.0
        )
        uom_categs = (consumed_moves | produced_moves).mapped(
            "product_uom_category_id"
        )
        mrp_force_exact_skip = self.env.context.get(
            "mrp_force_exact_skip", False
        )
        if len(uom_categs) == 1:
            qty_produced = sum(produced_moves.mapped("quantity"))
            qty_consumed = sum(
                move.product_uom._compute_quantity(
                    move.quantity, self.product_uom_id
                )
                for move in consumed_moves
            )
            if not float_is_zero(
                qty_consumed - qty_produced,
                precision_rounding=self.product_uom_id.rounding
            ):
                raise ValidationError(
                    _("For MO %s, consumed and produced quantities don't match (%.3f != %.3f)")
                    % (self.name, qty_consumed, qty_produced)
                )
