# © 2025 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html
from odoo import models, fields, api, _


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    def _get_default_category_id(self):
        context = self.env.context
        if context.get('product_categ_default_id'):
            return self.env.company.product_categ_default_id
        return super(ProductTemplate,self)._get_default_category_id()

    mdc_weight_dec_qty = fields.Float(
        string="Declared Weight",
        compute="_compute_mdc_weight_dec_qty",
        inverse="_inverse_mdc_weight_dec_qty",
    )

    mdc_category_check = fields.Boolean(
        string='Category Check',
        compute='_compute_mdc_category_check',
    )

    mdc_weight_dec_history = fields.One2many(
        comodel_name='mdc.weight.declared.weight',
        inverse_name='product_id',
        string='Declared Weight History',
    )

    @api.depends('categ_id', 'company_id.product_categ_default_id')
    def _compute_mdc_category_check(self):
        for product in self:
            product.mdc_category_check = (product.categ_id == self.env.user.company_id.product_categ_default_id)

    @api.depends("product_variant_ids.mdc_weight_dec_qty")
    def _compute_mdc_weight_dec_qty(self):
        for template in self.filtered('product_variant_ids'):
            template.mdc_weight_dec_qty = template.product_variant_ids[0].mdc_weight_dec_qty

    def _inverse_mdc_weight_dec_qty(self):
        for template in self.filtered('product_variant_ids'):
            template.product_variant_ids[0].mdc_weight_dec_qty = template.mdc_weight_dec_qty
