# © 2025 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html
from odoo import models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    def _get_default_category_id(self):
        context = self.env.context
        if context.get('product_categ_default_id'):
            return self.env.company.product_categ_default_id
        return super(ProductTemplate,self)._get_default_category_id()
