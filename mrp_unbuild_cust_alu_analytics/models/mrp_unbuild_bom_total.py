# © 2024 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3.0 (https://www.gnu.org/licenses/agpl-3.0.html)

from odoo import api, fields, models

class MrpBom(models.Model):
    _inherit = "mrp.unbuild.bom.totals"

    total_qty_percentage = fields.Float(
        widget="percent",
        compute="_compute_total_qty_percentage",
        store=True
    )

    @api.depends("total_qty", "unbuild_id.product_qty")
    def _compute_total_qty_percentage(self):
        for record in self:
            if record.unbuild_id.product_uom_id.category_id == record.bom_line_id.product_id.uom_id.category_id:
                record.total_qty_percentage = record.total_qty / record.unbuild_id.product_qty
            else:
                record.total_qty_percentage = 0
