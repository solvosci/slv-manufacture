# © 2024 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (https://www.gnu.org/licenses/lgpl-3.0.html)

from odoo import models, fields, api

class ProductProduct(models.Model):
    _inherit = "product.product"

    cost_management_residue = fields.Boolean(
        string='Has cost management residue',
        default=False,
        tracking=True,
        help="""
        When enabled, product residue will be covered with cost management
        """,
    )

    @api.depends('product_category_id.warehouse_valuation')
    def _compute_warehouse_valuation(self):
        for record in self:
            if not record.categ_id.warehouse_valuation:
                record.cost_management_residue = False
