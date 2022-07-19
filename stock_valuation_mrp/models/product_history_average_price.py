# © 2022 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (https://www.gnu.org/licenses/lgpl-3.0.html)

from odoo import models


class ProductHistoryAveragePrice(models.Model):
    _inherit = "product.history.average.price"

    def _from_svl_get_upd_svls_and_ret_phaps(self, svl):
        """
        From affected SVL, this function should return extra SVLs
        that should be updated and subsequent PHAP that should be
        recomputed.
        In this addon, we've got two case:
        * A production component price has changed, so production
          price has changed too
        * An unbuild, product unbuilded and the following created
          componentes changes their prices
        """
        upd_svls, ret_phaps = super()._from_svl_get_upd_svls_and_ret_phaps(svl)

        move = svl.stock_move_id
        # Production
        if move and move.raw_material_production_id:
            production_id = move.raw_material_production_id
            # - Consume SVL should simply be updated
            upd_svls |= svl
            # - Produce moves
            #   * PHAP is updated, so new price can be retrieved
            #   * SVLs are now updated and then not returned, but PHAP
            #     for production move must be updated
            prod_moves = production_id.move_finished_ids
            prod_price = prod_moves[0]._compute_production_svl_price(
                prod_moves[0].date
            )
            for svlp in prod_moves.stock_valuation_layer_ids:
                svlp.unit_cost = prod_price
                svlp.value = svlp.unit_cost * svlp.quantity
                ret_phaps |= svlp.history_average_price_id
        # Unbuild
        if move and move.unbuild_id and svl.quantity < 0.0:
            # We received the consumed move, it must be updated
            upd_svls |= svl
            # TODO better access to produced moves?
            prod_moves = move.unbuild_id.produce_line_ids.filtered(
                lambda x: sum(x.stock_valuation_layer_ids.mapped("quantity")) > 0.0
            )
            # The related consumes also will be updated, so PHAP will vary
            upd_svls |= prod_moves.stock_valuation_layer_ids

            ret_phaps |= prod_moves.stock_valuation_layer_ids.mapped(
                "history_average_price_id"
            )

        return upd_svls, ret_phaps
