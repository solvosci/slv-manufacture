# © 2024 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (https://www.gnu.org/licenses/lgpl-3.0.html)

from odoo import _, models


class MrpUnbuildBomTotals(models.Model):
    _inherit = 'mrp.unbuild.bom.totals'

    def action_mrp_unbuild_bom_quants_views(self):
        return {
            'type': 'ir.actions.act_window',
            'name': self.bom_line_id.product_id.name,
            'res_model': 'mrp.unbuild.bom.quants',
            'view_mode': 'tree',
            'view_id': self.env.ref("mrp_unbuild_advanced.mrp_unbuild_bom_quants_reduced_view").id,
            'domain': ['&', ('bom_line_id', '=', self.bom_line_id.id), ('unbuild_id', '=', self.unbuild_id.id)],
        }
