# © 2024 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (https://www.gnu.org/licenses/lgpl-3.0.html)

from odoo import api, fields, models

class MrpBom(models.Model):
    _inherit = "mrp.unbuild.bom.totals"

    total_qty_percentage = fields.Float(
        widget="percent",
        compute="_compute_total_qty_percentage",
        store=True
    )

    @api.depends("expected_qty")
    def _compute_total_qty_percentage(self):
        for record in self:
            record.total_qty_percentage = record.total_qty / record.unbuild_id.product_qty
