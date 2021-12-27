# © 2021 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (https://www.gnu.org/licenses/lgpl-3.0.html)

from odoo import models
from odoo.tools import float_is_zero


class StockMove(models.Model):
    _inherit = "stock.move"

    def _unlink_previous_stuff(self):
        super()._unlink_previous_stuff()
        # SVL deletion, and then, we're able to update Standard Price
        # Inspired on stock.move Odoo default product_price_update_before_done method
        for move_id in self.filtered(
            lambda move: move._is_in()
            and move.with_context(
                force_company=move.company_id.id
            ).product_id.cost_method == "average"
        ):
            quantity_slv = move_id.product_id.sudo().with_context(
                force_company=move_id.company_id.id
            ).quantity_svl
            std_price = move_id.product_id.with_context(
                force_company=move_id.company_id.id
            ).standard_price

            # TODO compute quantity stuff?
            quantity_slv_unlink = sum(
                move_id.stock_valuation_layer_ids.mapped("quantity")
            )
            value_slv_unlink = sum(
                move_id.stock_valuation_layer_ids.mapped("value")
            )

            # Very corner case?
            new_std_price = 0.0
            if not float_is_zero(
                quantity_slv - quantity_slv_unlink,
                precision_rounding=move_id.product_id.uom_id.rounding
            ):
                new_std_price = (
                    (quantity_slv*std_price - value_slv_unlink) /
                    (quantity_slv - quantity_slv_unlink)
                )

            move_id.product_id.with_context(
                force_company=move_id.company_id.id
            ).sudo().write({"standard_price": new_std_price})

        self.sudo().stock_valuation_layer_ids.unlink()
