# © 2024 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (https://www.gnu.org/licenses/lgpl-3.0.html)

from odoo import api, fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    process_type_ids = fields.Many2many(
        'mrp.unbuild.process.type',
        string='Process types',
        compute='_compute_process_type_ids',
        store=True,
    )

    @api.depends('bom_ids.process_type_id')
    def _compute_process_type_ids(self):
        for product in self:
            product.process_type_ids = product.bom_ids.mapped('process_type_id')
