# © 2023 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (https://www.gnu.org/licenses/lgpl-3.0.html)

from odoo import _, models
from odoo.exceptions import ValidationError
from odoo.tools import float_is_zero


class MrpUnbuild(models.Model):
    _inherit = "mrp.unbuild"

    def action_unbuild(self):
        ret = super().action_unbuild()
        # We'll only check quantities that belong to the same UoM category.
        #  Other operation should be inconsistent
        line_ids = self.produce_line_ids.filtered(
            lambda x: x.product_uom_category_id == self.product_id.uom_id.category_id
        )
        move_consumed = line_ids.filtered(
            lambda x: x.location_dest_id.usage == "production"
        )
        move_produced = (line_ids - move_consumed)
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
