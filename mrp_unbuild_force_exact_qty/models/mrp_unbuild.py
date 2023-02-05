# © 2023 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (https://www.gnu.org/licenses/lgpl-3.0.html)

from odoo import _, models
from odoo.exceptions import ValidationError
from odoo.tools import float_is_zero


class MrpUnbuild(models.Model):
    _inherit = "mrp.unbuild"

    def action_unbuild(self):
        ret = super().action_unbuild()
        # We'll only check quantities if every consumed and produced move
        #  belongs to the same UoM cateogory. Other operation should be
        #  inconsistent
        uom_categs = self.produce_line_ids.mapped("product_uom_category_id")
        if len(uom_categs) == 1:
            move_consumed = self.produce_line_ids.filtered(
                lambda x: x.product_id == self.product_id
            )
            move_produced = (self.produce_line_ids - move_consumed)
            qty_consumed = sum(move_consumed.mapped("quantity_done"))
            qty_produced = sum(
                move.product_uom._compute_quantity(
                    move.quantity_done, self.product_uom_id
                )
                for move in move_produced
            )
            if not float_is_zero(
                qty_consumed - qty_produced,
                precision_rounding=self.product_uom_id.rounding
            ):
                raise ValidationError(
                    _("Unbuild and generated quantities don't match (%.3f != %.3f)")
                    % (qty_consumed, qty_produced)
                )
        return ret
