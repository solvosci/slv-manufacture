# © 2024 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (https://www.gnu.org/licenses/lgpl-3.0.html)

from odoo import models, fields, api

class ProductTemplate(models.Model):
    _inherit = "product.template"

    cost_management_residue = fields.Boolean(
        string='Has cost management residue',
        default=False,
        tracking=True,
        compute='_compute_cost_management_residue',
        inverse='_set_cost_management_residue',
        store=True,
        help="""
        When enabled, operations from/to this warehouse will be covered,
        such as internal transfers, incomings, productions, etc.
        """,
    )

    @api.depends("cost_management_residue", "warehouse_valuation")
    def _compute_cost_management_residue(self):
        unique_variants = self.filtered(lambda template: len(template.product_variant_ids) == 1)
        for template in unique_variants:
            if template.warehouse_valuation:
                template.cost_management_residue = template.product_variant_ids.cost_management_residue
            else:
                template.cost_management_residue = False
        for template in (self - unique_variants):
            template.cost_management_residue = False

    def _set_cost_management_residue(self):
        for template in self:
            if len(template.product_variant_ids) == 1:
                template.product_variant_ids.cost_management_residue = template.cost_management_residue
