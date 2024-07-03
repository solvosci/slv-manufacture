# © 2022 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (https://www.gnu.org/licenses/lgpl-3.0.html)

import logging

from odoo import models

logger = logging.getLogger(__name__)


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

    def _compute_unbuild_svl_unit_cost(self, phap_price):
        # Override by other modules
        return phap_price

    def _compute_unbuild_svl_quantity(self, quantity):
        # Override by other modules
        return quantity

    def _unlink_previous_stuff(self):
        """
        When an unbuild is undone (moved to "draft" state again), stock moves
        will be removed.
        In this case,
        * SVLs should be deleted
        * PHAP for moves date and later will be affected
        * Other SVLs (because of PHAP changes) will be affected too
        """
        super()._unlink_previous_stuff()

        moves = self.filtered(lambda x: x.product_id.warehouse_valuation)
        # Every SVL will be deleted, but only those that are linked to
        #  incoming moves are important fot later PHAPs recalculation
        svls = moves.sudo().stock_valuation_layer_ids
        phaps = svls.mapped("history_average_price_id")

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

        moves._compute_phaps_and_update_slvs(phaps=phaps)

    def _init_phaps(self):
        """
        Initialize PHAPs firing computation from initial purchase & transfer
        inputs for every (product, warehouse), based on initial valued SVLs
        EXECUTE AS SUPERUSER
        DO NOT USE BUT ON ADDON STARTUP
        """
        super()._init_phaps()

        # *********************************************************************
        # *************************** UNBUILDS ********************************
        sql_initial_unbuilds = """
            select
                slv2.stock_move_id smid, V.*
            from (
                select
                    svl.product_id, svl.warehouse_id, min(svl.create_date) min_date 
                from
                    stock_valuation_layer svl
                inner join
                    stock_move sm on sm.id=svl.stock_move_id
                where
                    sm.state='done' and
                    sm.unbuild_id is not null and
                    svl.quantity > 0
                group by
                    svl.product_id, svl.warehouse_id
                order by
                    min_date
            ) V
            inner join
                stock_valuation_layer slv2 on
                    slv2.product_id=V.product_id and
                    slv2.warehouse_id=V.warehouse_id and
                    slv2.create_date=V.min_date
            order by
                V.min_date
            """
        self.env.cr.execute(sql_initial_unbuilds)
        init_usm_ids = []
        for row in self.env.cr.dictfetchall():
            init_usm_ids.append(row["smid"])

        logger.info(
            "_init_phaps: running _compute_phaps_and_update_slvs()"
            " for %d initial unbuilds..."
            % len(init_usm_ids)
        )
        self.browse(init_usm_ids)._compute_phaps_and_update_slvs()
        logger.info(
            "_init_phaps: finished _compute_phaps_and_update_slvs()"
            " for initial unbuilds!"
        )
        # *********************************************************************

        # *********************************************************************
        # ************************* PRODUCTIONS *******************************
        sql_initial_mrps = """
            select
                slv2.stock_move_id smid, V.*
            from (
                select
                    svl.product_id, svl.warehouse_id, min(svl.create_date) min_date 
                from
                    stock_valuation_layer svl
                inner join
                    stock_move sm on sm.id=svl.stock_move_id
                where
                    sm.state='done' and
                    sm.production_id is not null
                group by
                    svl.product_id, svl.warehouse_id
                order by
                    min_date
            ) V
            inner join
                stock_valuation_layer slv2 on
                    slv2.product_id=V.product_id and
                    slv2.warehouse_id=V.warehouse_id and
                    slv2.create_date=V.min_date
            order by
                V.min_date
            """
        self.env.cr.execute(sql_initial_mrps)
        sql_initial_mrps = []
        for row in self.env.cr.dictfetchall():
            sql_initial_mrps.append(row["smid"])

        logger.info(
            "_init_phaps: running _compute_phaps_and_update_slvs()"
            " for %d initial productions..."
            % len(sql_initial_mrps)
        )
        self.browse(sql_initial_mrps)._compute_phaps_and_update_slvs()
        logger.info(
            "_init_phaps: finished _compute_phaps_and_update_slvs()"
            " for initial productions!"
        )
        # *********************************************************************
