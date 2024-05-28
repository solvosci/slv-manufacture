# © 2024 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (https://www.gnu.org/licenses/lgpl-3.0.html)

from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _compute_unbuild_svl_unit_cost(self, phap_price):
        if self.unbuild_id:
            return self.unbuild_id.cost_unit_price
        return phap_price

    def _compute_unbuild_svl_quantity(self, quantity):
        # Two cases for a SVL zero quantity, when move comes from a produced unbuild:
        # - Product is a waste one
        # - Move came from a quant total marked => we have no direct link for this
        # TODO at mrp_unbuild_bom_cust_qty consider link a created stock move with
        #      origin quant total
        self.ensure_one()
        if self.product_id.has_waste_cost_mgmt:
            return 0.0
        quant_total = self.unbuild_id.bom_quants_total_ids.filtered(
            lambda x: x.bom_line_id.product_id == self.product_id
        )
        # TODO it should be only one, but...
        if quant_total and quant_total[0].disabled_mrp_unbuild_valuation:
            return 0.0
        return quantity
