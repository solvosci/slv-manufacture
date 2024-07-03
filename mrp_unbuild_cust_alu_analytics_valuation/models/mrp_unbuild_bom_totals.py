# © 2024 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (http://www.gnu.org/licenses/lgpl-3.0.html)

from odoo import models, fields, api


class MrpUnbuildBoMTotals(models.Model):
    _inherit = "mrp.unbuild.bom.totals"

    disabled_mrp_unbuild_valuation = fields.Boolean(
        string='Disabled for manufacturing/unbuild valuation',
    )

    @api.model_create_multi
    def create(self, vals_list):
        bom_line_obj = self.env["mrp.bom.line"]
        for vals in vals_list:
            bom_line = vals.get("bom_line_id", False)
            if bom_line:
                vals.setdefault(
                    "disabled_mrp_unbuild_valuation",
                    bom_line_obj.browse(bom_line).disabled_mrp_unbuild_valuation
                )
        return super().create(vals_list)
