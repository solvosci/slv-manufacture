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
        # TODO if move is linked to a non-valuable LdM product,
        #      return 0 is needed
        return (
            (not self.product_id.has_waste_cost_mgmt)
            and quantity
            or 0.0
        )
