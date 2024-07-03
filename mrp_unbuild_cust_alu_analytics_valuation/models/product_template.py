# © 2024 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (https://www.gnu.org/licenses/lgpl-3.0.html)

from odoo import models, fields, api

class ProductTemplate(models.Model):
    _inherit = "product.template"

    has_waste_cost_mgmt = fields.Boolean(
        string='Has cost management residue',
        default=False,
        tracking=True,
        compute='_compute_has_waste_cost_mgmt',
        inverse='_set_has_waste_cost_mgmt',
        store=True,
        readonly=False,
        help="""
        When enabled, operations from/to this warehouse will be covered,
        such as internal transfers, incomings, productions, etc.
        """,
    )
    waste_mgmt_pricelist_id = fields.Many2one(
        comodel_name='product.pricelist',
        string='Pricelist for management residue',
        default=False,
        tracking=True,
        compute='_compute_waste_mgmt_pricelist_id',
        inverse='_set_waste_mgmt_pricelist_id',
        store=True,
        readonly=False,
        help="""
        Pricelist used for cost management residue
        """,
    )

    def _compute_has_waste_cost_mgmt(self):
        unique_variants = self.filtered(lambda template: len(template.product_variant_ids) == 1)
        for template in unique_variants:
            if template.warehouse_valuation:
                template.has_waste_cost_mgmt = template.product_variant_ids.has_waste_cost_mgmt
            else:
                template.has_waste_cost_mgmt = False
        for template in (self - unique_variants):
            template.has_waste_cost_mgmt = False

    def _set_has_waste_cost_mgmt(self):
        for template in self:
            if len(template.product_variant_ids) == 1:
                template.product_variant_ids.has_waste_cost_mgmt = template.has_waste_cost_mgmt

    def _compute_waste_mgmt_pricelist_id(self):
        unique_variants = self.filtered(lambda template: len(template.product_variant_ids) == 1)
        for template in unique_variants:
            if template.waste_mgmt_pricelist_id:
                template.waste_mgmt_pricelist_id = template.product_variant_ids.waste_mgmt_pricelist_id
            else:
                template.waste_mgmt_pricelist_id = False
        for template in (self - unique_variants):
            template.waste_mgmt_pricelist_id = False

    def _set_waste_mgmt_pricelist_id(self):
        for template in self:
            if len(template.product_variant_ids) == 1:
                template.product_variant_ids.waste_mgmt_pricelist_id = template.waste_mgmt_pricelist_id

    @api.model_create_multi
    def create(self, vals_list):
        templates = super().create(vals_list)
        for template, vals in zip(templates, vals_list):
            related_vals = {}
            if vals.get("has_waste_cost_mgmt"):
                related_vals["has_waste_cost_mgmt"] = vals["has_waste_cost_mgmt"]
            if vals.get("waste_mgmt_pricelist_id"):
                related_vals["waste_mgmt_pricelist_id"] = vals("waste_mgmt_pricelist_id")
            if related_vals:
                template.write(related_vals)
        return templates

    @api.onchange("has_waste_cost_mgmt")
    def _onchange_has_waste_cost_mgmt(self):
        for template in self:
            if not template.has_waste_cost_mgmt:
                template.waste_mgmt_pricelist_id = False
