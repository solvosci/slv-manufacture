# © 2024 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3.0 (https://www.gnu.org/licenses/agpl-3.0.html)

from odoo import api, models
from odoo.exceptions import UserError


class QcTest(models.Model):
    _inherit = "qc.test"

    @api.ondelete(at_uninstall=False)
    def _unlink_test_reference(self):
        qc_test_xml_ids = self.get_external_id().values()
        if "mrp_unbuild_cust_alu_analytics.qc_test_1" in qc_test_xml_ids:
            raise UserError("Deleting default qc_test for Analytics is not allowed.")
