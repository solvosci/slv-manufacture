# © 2022 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See https://www.gnu.org/licenses/lgpl-3.0.html

from odoo import api, fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    component_bom_ids = fields.Many2many(
        comodel_name="mrp.bom",
        compute="_compute_component_bom_ids",
        string="BoMs that have this product in a BoM line",
    )

    def write(self, values):
        """
        When standard_price changes for a product, we look for those BoMs
        that belogs to, and we'll force the standard_product recalculation
        for the affected products (the BoMs product)
        """
        res = super(ProductProduct, self).write(values)
        if "standard_price" in values.keys():
            bom_ids = self.env["mrp.bom"]
            for product in self.sudo():
                bom_ids |= product.component_bom_ids
            # This probably cause new standard_price write() events
            #  and some same standard_price, but it seems not to be a problem
            bom_ids.update_product_standard_price()

        return res
        
    def _compute_component_bom_ids(self):
        obj_bomlines = self.env["mrp.bom.line"]
        # TODO search_read for better performance
        for product in self:
            product.component_bom_ids = obj_bomlines.search(
                [("product_id", "=", product.id)]
            ).mapped("bom_id").filtered(lambda x: x.active)
