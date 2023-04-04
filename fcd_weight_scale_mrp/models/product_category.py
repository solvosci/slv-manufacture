# © 2022 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html

from odoo import models, fields


class ProductCategory(models.Model):
    _inherit = "product.category"

    fcd_type = fields.Selection([("fish", "Fish"), ("crustaceans_sulphites", "Crustaceans and sulphites"), ("molluscs", "Molluscs")])

    def get_fcd_type(self):
        categories = [self]
        type = False
        for categ in categories:
            if categ.fcd_type in ["fish", "crustaceans_sulphites", "molluscs"]:
                type = categ.fcd_type
                break
            if categ.parent_id:
                categories.append(categ.parent_id)
        return type
