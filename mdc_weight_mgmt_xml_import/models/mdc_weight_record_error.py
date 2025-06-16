# © 2025 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import models, fields


class MdcWeightRecordError(models.Model):
    _name = 'mdc.weight.record.error'
    _description = 'Errors from XML import'
    _inherit = ['mail.thread']
    _order = 'create_date desc, reviewed asc'

    company_id = fields.Many2one(
        'res.company',
        default=lambda self: self.env.company,
    )
    equipment_id = fields.Many2one(
        'maintenance.equipment',
        string="Line",
        help="Equipment line associated with the error.",
    )
    file_name = fields.Char()
    error_message = fields.Text()
    traceback = fields.Text()
    reviewed = fields.Boolean(
        default=False,
        help="Indicates if the error has been reviewed by a user.",
        tracking=True,
    )

    def _set_reviewed(self, value):
        self.sudo().write({'reviewed': value})

    def action_check_review(self):
        self._set_reviewed(True)

    def action_cancel_review(self):
        self._set_reviewed(False)

    def action_send_mail(self):
        if not self:
            return
        template = self.env.ref('mdc_weight_mgmt_xml_import.email_template_xml_import_error_notification')
        template.with_context(error_list=self).send_mail(self[0].id, force_send=True)
