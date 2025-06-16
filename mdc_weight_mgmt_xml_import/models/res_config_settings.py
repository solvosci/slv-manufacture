# © 2025 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    mdc_notify_error_partner_ids = fields.Many2many(
        related='company_id.mdc_notify_error_partner_ids',
        string="Notify on Error",
        readonly=False
    )

class ResCompany(models.Model):
    _inherit = 'res.company'

    mdc_notify_error_partner_ids = fields.Many2many(
        'res.partner',
        string="Notify on Error",
        help="Partners to notify when an error occurs during XML import.",
        domain="[('email', '!=', False)]"
    )
