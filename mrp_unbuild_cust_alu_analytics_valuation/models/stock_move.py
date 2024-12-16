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
    
    def _get_move_cost(self):
        """
        Obtains move cost based on its move lines.
        When a move line uniquely linked to an unbuild cost is obtained
        from such unbuild; if not, from valuation layer
        """
        self.ensure_one()
        cost = 0.0
        for ml in self.move_line_ids.filtered(lambda x: x.state == "done"):
            unbuild_id = ml.move_id._get_move_line_cost_unbuild_ids(ml)
            if len(unbuild_id) == 1:
                cost += unbuild_id.cost_unit_price * ml.qty_done
            else:
                # TODO if there's more than one valuation layer?
                cost += ml.qty_done * (
                    self.stock_valuation_layer_ids
                    and self.stock_valuation_layer_ids[0].unit_cost
                    or 0.0
                )

        return cost
    
    def _get_move_line_cost_unbuild_ids(self, ml):
        # TODO move to stock_move_line.py, and ml should be self
        return ml.lot_id and ml.search([
            ("lot_id", "=", ml.lot_id.id),
            ("move_id.unbuild_id", "!=", False),
            ("location_id.usage", "=", "production"),
            ("state", "=", "done"),
        ]).move_id.unbuild_id or self.env["mrp.unbuild"]
        
    def _get_move_income_price_unit(self):
        # TODO it should be price AND product_uom_id
        self.ensure_one()
        sale_line_id = (
            "sale_line_id" in self
            and self["sale_line_id"]
            or False
        )
        if sale_line_id:
            return sale_line_id.price_unit
        else:
            return 0.0
