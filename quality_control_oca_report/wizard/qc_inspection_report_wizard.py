# © 2026 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0.html

from odoo import models, fields, api, Command


class QcInspectionReportWizard(models.TransientModel):
    _name = 'qc.inspection.report.wizard'
    _description = 'Wizard to create a quality control report'

    inspection_id = fields.Many2one('qc.inspection', string="Inspection", required=True)
    title = fields.Char(string="Title", default="")
    description = fields.Text(string="Description")

    image_ids = fields.Many2many(
            'ir.attachment', 'wizard_inspection_images_rel',
            string="Images to attach",
            domain=[('mimetype', 'ilike', 'image')],
            help="Images (JPEG, PNG, etc.) that will be attached to the inspection report"
        )
    # document_ids = fields.Many2many(
    #     'ir.attachment', 'wizard_inspection_docs_rel',
    #     string="Documents to attach",
    #     domain=[('mimetype', 'not ilike', 'image')],
    #     help="Documents (PDF, Excel, etc.) that will be attached to the inspection report"
    # )

    @api.model
    def default_get(self, fields_list):
        res = super(QcInspectionReportWizard, self).default_get(fields_list)
        inspection_id = self.env.context.get('active_id')

        if inspection_id:
            inspection = self.env['qc.inspection'].browse(inspection_id)
            res['inspection_id'] = inspection.id
            res['description'] = inspection.external_notes

            existing_attachments = self.env['ir.attachment'].search([
                ('res_model', '=', 'qc.inspection'),
                ('res_id', '=', inspection.id)
            ])
            images = existing_attachments.filtered(lambda a: 'image' in (a.mimetype or ''))
            # documents = existing_attachments - images

            res['image_ids'] = [Command.set(images.ids)]
            # res['document_ids'] = [Command.set(documents.ids)]
        return res

    def action_confirm_report(self):
        self.ensure_one()
        all_wizard_attachments = self.image_ids  # + self.document_ids
        new_files = all_wizard_attachments.filtered(lambda a: not a.res_id)
        if new_files:
            new_files.write({
                'res_model': 'qc.inspection',
                'res_id': self.inspection_id.id,
            })
        return self.env.ref('quality_control_oca_report.action_report_qc_incidence').report_action(self)
