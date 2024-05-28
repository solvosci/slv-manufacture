# © 2024 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (http://www.gnu.org/licenses/lgpl-3.0.html)

from odoo import models, fields, api


class MrpUnbuildBoMTotals(models.Model):
    _inherit = "mrp.unbuild.bom.totals"

    disabled_mrp_unbuild_valuation = fields.Boolean(
        string='Disabled for manufacturing/unbuild valuation',
    )

    disabled_mrp_unbuild_valuation_readonly = fields.Boolean(
        compute="_compute_disabled_mrp_unbuild_valuation_readonly",
    )

    @api.model
    def _get_mrp_unbuild_valuation_to_disable(self, bom_line_id):
        return (
            bom_line_id.disabled_mrp_unbuild_valuation
            or bom_line_id.product_id.has_waste_cost_mgmt
            or bom_line_id.product_id.type not in ["product", "consu"]
        )

    def _compute_disabled_mrp_unbuild_valuation_readonly(self):
        total_ro = self.filtered(lambda x: (
            x.unbuild_id.state == "done"
            or x.bom_line_id._get_mrp_unbuild_valuation_to_disable()
        ))
        total_ro.write({
            "disabled_mrp_unbuild_valuation_readonly": True,
        })
        (self - total_ro).write({
            "disabled_mrp_unbuild_valuation_readonly": False,
        })

    @api.model_create_multi
    def create(self, vals_list):
        bom_line_obj = self.env["mrp.bom.line"]
        for vals in vals_list:
            bom_line = vals.get("bom_line_id", False)
            if bom_line:
                bom_line_id = bom_line_obj.browse(bom_line)
                vals.setdefault(
                    "disabled_mrp_unbuild_valuation",
                    bom_line_id._get_mrp_unbuild_valuation_to_disable()
                )
        return super().create(vals_list)
