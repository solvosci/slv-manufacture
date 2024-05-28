# © 2024 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (https://www.gnu.org/licenses/lgpl-3.0.html)

from odoo import models, fields, api

class ProductProduct(models.Model):
    _inherit = "product.product"

    has_waste_cost_mgmt = fields.Boolean(
        string='Has cost management residue',
        default=False,
        tracking=True,
        readonly=False,
        compute='_compute_has_waste_cost_mgmt',
        store=True,
        help="""
        When enabled, product residue will be covered with cost management
        """,
    )

    waste_mgmt_pricelist_id = fields.Many2one(
        comodel_name='product.pricelist',
        string='Pricelist for management residue',
        tracking=True,
        readonly=False,
        compute='_compute_waste_mgmt_pricelist_id',
        store=True,
        help="""
        Pricelist used for cost management residue
        """,
    )

    @api.depends("categ_id.warehouse_valuation")
    def _compute_has_waste_cost_mgmt(self):
        valuation_products = self.filtered(lambda x: x.warehouse_valuation == False and x.has_waste_cost_mgmt == True)
        valuation_products.write(
            {"has_waste_cost_mgmt": False}
        )


    @api.depends("has_waste_cost_mgmt")
    def _compute_waste_mgmt_pricelist_id(self):
        valuation_products = self.filtered(lambda x: x.has_waste_cost_mgmt == False and x.waste_mgmt_pricelist_id != False)
        valuation_products.write(
            {"waste_mgmt_pricelist_id": False}
        )

    def write(self, values):
        return super().write(values)

    # @api.onchange("has_waste_cost_mgmt")
    # def _onchange_has_waste_cost_mgmt(self):
    #     for product in self:
    #         if not product.has_waste_cost_mgmt:
    #             product.waste_mgmt_pricelist_id = False
