# © 2022 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See https://www.gnu.org/licenses/lgpl-3.0.html

from odoo import api, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    def write(self, values):
        """
        When a product becomes standard, average price should be recalculated
        """
        res = super(ProductTemplate, self).write(values)
        if "categ_id" in values.keys():
            new_categ = self.env["product.category"].browse(values["categ_id"])
            if new_categ.property_cost_method == "standard":
                bom_ids = self.env["mrp.bom"]
                for tmpl in self.sudo():
                    bom_ids |= tmpl.bom_ids
                bom_ids.update_product_standard_price()

        return res
