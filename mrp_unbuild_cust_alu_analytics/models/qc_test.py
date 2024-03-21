# © 2024 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3.0 (https://www.gnu.org/licenses/agpl-3.0.html)

from odoo import fields, models, api
from odoo.exceptions import UserError

class QcTest(models.Model):
    _inherit = "qc.test"

    def unlink(self):
        for record in self:
            if  list(record.get_external_id().values())[0] == 'mrp_unbuild_cust_alu_analytics.qc_test_1':
                raise UserError("Deleting default qc_test for Analytics is not allowed.")
            return super(QcTest, self).unlink()
