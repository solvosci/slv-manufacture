# © 2025 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html
from odoo import models, fields


class ResCompany(models.Model):
    _inherit = "res.company"

    product_categ_default_id = fields.Many2one(
        comodel_name="product.category",
        string="Default product category",
    )
    equipment_category_default_id = fields.Many2one(
        comodel_name="maintenance.equipment.category",
        string="Default equipment category",
    )
    image_logo_template =  fields.Binary(
        string="Image Logo",
    )

class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    product_categ_default_id = fields.Many2one(
        string="Default product category",
        related="company_id.product_categ_default_id",
        readonly=False,
    )

    equipment_category_default_id = fields.Many2one(
        string="Default equipment category",
        related="company_id.equipment_category_default_id",
        readonly=False,
    )

    image_logo_template =  fields.Binary(
        string="Image Logo",
        related="company_id.image_logo_template",
        readonly=False
    )
