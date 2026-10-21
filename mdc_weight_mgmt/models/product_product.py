# © 2025 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
class ProductProduct(models.Model):
    _inherit = 'product.product'

    mdc_weight_dec_history = fields.One2many(
        comodel_name='mdc.weight.declared.weight',
        inverse_name='product_id',
        string='Declared Weight History',
    )

    mdc_weight_dec_qty = fields.Float(
        string='Declared Weight',
        required=True
    )

    @api.constrains("mdc_weight_dec_qty","categ_id")
    def _check_mdc_weight_dec_qty(self):
        products_ko_weight_dec_qty = self.filtered(lambda x: x.mdc_weight_dec_qty <= 0 and x.mdc_category_check)
        if products_ko_weight_dec_qty:
            raise ValidationError(_("The declared weight must be greater than 0."))
