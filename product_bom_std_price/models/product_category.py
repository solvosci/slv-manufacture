# © 2022 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See https://www.gnu.org/licenses/lgpl-3.0.html

from odoo import api, models


class ProductCategory(models.Model):
    _inherit = "product.category"

    @api.multi
    def write(self, values):
        """
        When a product cost method becomes standard, the average price must be
        recalculated
        """
        ret = super(ProductCategory, self).write(values)
        if values.get("property_cost_method", False) == "standard":
            products = self.env["product.product"].search(
                [("categ_id", "in", self.ids)]
            )
            boms = products.sudo().mapped("component_bom_ids")
            if boms:
                boms.update_product_standard_price()
        return ret
        
