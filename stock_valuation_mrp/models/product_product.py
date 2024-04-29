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

    residue_pricelist_mgmt = fields.Many2one(
        comodel_name='product.pricelist',
        string='Pricelist for management residue',
        default=False,
        tracking=True,
        readonly=False,
        compute='_compute_residue_pricelist_mgmt',
        store=True,
        help="""
        Pricelist used for cost management residue
        """,
    )

    @api.depends("categ_id.warehouse_valuation")
    def _compute_has_waste_cost_mgmt(self):
        for product in self:
            product.has_waste_cost_mgmt = False # Allways False if warehouse_valuation change (True or False)


    @api.depends("has_waste_cost_mgmt")
    def _compute_residue_pricelist_mgmt(self):
        for product in self:
            product.residue_pricelist_mgmt = False # Same as above

    def write(self, values):
        if "categ_id" in values and "has_waste_cost_mgmt" not in values:
            new_categ = self.env["product.category"].browse(values["categ_id"])
            values["has_waste_cost_mgmt"] = False
        if "categ_id" in values and "residue_pricelist_mgmt" not in values:
            new_categ = self.env["product.category"].browse(values["categ_id"])
            values["residue_pricelist_mgmt"] = False
        return super().write(values)

    @api.onchange("has_waste_cost_mgmt")
    def _onchange_has_waste_cost_mgmt(self):
        for product in self:
            if not product.has_waste_cost_mgmt:
                product.residue_pricelist_mgmt = False
