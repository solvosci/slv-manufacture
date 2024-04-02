# © 2024 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3.0 (https://www.gnu.org/licenses/agpl-3.0.html)

from odoo import fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    xml_analytic_path = fields.Char(
        related='company_id.xml_analytic_path',
        readonly=False,
    )

class ResCompany(models.Model):
    _inherit = 'res.company'

    xml_analytic_path = fields.Char(
        string="XML Analytic Path",
        readonly=False
    )
