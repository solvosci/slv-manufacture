# © 2022 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html

from odoo import models, fields


class ProductTemplate(models.Model):
    _inherit = "product.template"

    production_secondary_uom_id = fields.Many2one(
        comodel_name="product.secondary.unit",
        compute="_compute_production_secondary_uom_id",
        string="Second unit for production"
    )

    def _compute_production_secondary_uom_id(self):
        for record in self:
            if record.secondary_uom_ids.filtered(lambda x: x.factor == 0):
                record.production_secondary_uom_id = record.secondary_uom_ids.filtered(lambda x: x.factor == 0)[0]
            else:
                record.production_secondary_uom_id = False


class ProductProduct(models.Model):
    _inherit = "product.product"

    production_secondary_uom_id = fields.Many2one(
        comodel_name="product.secondary.unit",
        string="Second unit for production",
        related="product_tmpl_id.production_secondary_uom_id",
    )