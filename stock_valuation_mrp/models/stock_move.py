# © 2022 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (https://www.gnu.org/licenses/lgpl-3.0.html)

from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _action_done(self, cancel_backorder=False):
        done_moves = self.browse()

        production_moves = self.filtered(
            lambda x: (
                x.raw_material_production_id
                or x.production_id
            ) and x.product_id.warehouse_valuation
        )
        if production_moves:
            # It's possible to have different productions
            mrps = (
                production_moves.mapped("raw_material_production_id") |
                production_moves.mapped("production_id")
            )
            for mrp in mrps:
                # FOR TESTING PURPOSES, ref date is planned start date
                moves = production_moves.filtered(
                    lambda x: x.raw_material_production_id.id == mrp.id
                    or x.production_id.id == mrp.id
                ).with_context(
                    stock_move_custom_date=mrp.date_planned_start
                )
                done_moves |= super(StockMove, moves)._action_done(
                    cancel_backorder=cancel_backorder
                )

        done_moves |= super(StockMove, self - production_moves)._action_done(
            cancel_backorder=cancel_backorder
        )
        return done_moves

    def _compute_production_svl_price(self, date):
        """
        For this production move, gets custom average price
        based on current PHAP for components and their quantities
        """
        self.ensure_one()
        PHAP_sudo = self.env["product.history.average.price"].sudo()
        total_amount = 0
        total_qtys = 0
        raw_ids = self.production_id.move_raw_ids
        for component in raw_ids:
            total_amount += PHAP_sudo.get_price(
                component.product_id,
                component.location_id.get_warehouse(),
                dt=date
            ) * component.quantity_done
            total_qtys += component.quantity_done
        # TODO divide by zero, is it possible?
        return total_amount / total_qtys

    def _unlink_previous_stuff(self):
        """
        When an unbuild is undone (moved to "draft" state again), stock moves
        will be removed.
        In this case,
        * SVLs should be deleted
        * PHAP for moves date and later will be affected
        * Other SVLs (because of PHAP changes) will be affected too
        This process only makes sense for destination moves (the components
        created before), because they're the inputs
        """
        super()._unlink_previous_stuff()

        in_moves = self.filtered(
            lambda x: x._is_in()
            and x.product_id.warehouse_valuation
        )
        # Every SVL will be deleted, but only those that are linked to
        #  incoming moves are important fot later PHAPs recalculation
        svls_in = in_moves.sudo().stock_valuation_layer_ids
        phaps = svls_in.mapped("history_average_price_id")

        self.sudo().stock_valuation_layer_ids.unlink()

        # Account Move deletion: before deleting them they must be
        #  cancelled or drafted (previously not posted) => we ensure
        #  they're all cancelled
        acct_moves = self.sudo().account_move_ids
        acct_moves_posted = acct_moves.filtered(lambda x: x.state == "posted")
        if acct_moves_posted:
            acct_moves_posted.button_draft()
        acct_moves.filtered(lambda x: x.state != "cancel").button_cancel()
        acct_moves.with_context(force_delete=True).unlink()

        in_moves._compute_phaps_and_update_slvs(phaps=phaps)
