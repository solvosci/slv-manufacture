# © 2023 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html

from odoo import api, models, _

class ReportBomPreviewStructure(models.AbstractModel):
    _name = 'report.mrp_production_bom_preview_report.mrp_preview_bom_report'
    _description = 'Structure Report'

    @api.model
    def get_html(self, mo=False):
        res = {}
        res['mo'] = self.env['mrp.production'].browse(mo)
        res['report_type'] = 'html'
        res['report_structure'] = 'all'
        res['order'] = self.env.ref('mrp_production_bom_preview_report.mrp_preview_bom_report')._render({'data': res})
        return res
