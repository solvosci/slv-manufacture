# © 2025 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import models


class MdcWeightRecordReportWizard(models.TransientModel):
    _inherit = 'mdc.weight.record.report.wizard'

    def action_mdc_weight_report_xlsx(self):
        self._validate_report_data()
        return self.env.ref('mdc_weight_mgmt_xlsx_report.action_mdc_weight_report_xlsx').report_action(self)
