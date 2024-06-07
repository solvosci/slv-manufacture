# © 2024 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3.0 (https://www.gnu.org/licenses/agpl-3.0.html)

from odoo import api, fields, models

class QcInspectionLine(models.Model):
    _inherit = "qc.inspection.line"
    _description = "Quality control inspection line"
    
    minor = fields.Boolean(
        string='Minor',
        default=False
    )
