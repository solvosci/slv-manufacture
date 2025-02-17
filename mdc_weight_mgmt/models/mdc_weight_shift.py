# © 2025 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html
from odoo import models, fields


class MdcWeightShift(models.Model):
    _name = 'mdc.weight.shift'
    _inherit = ['mail.thread']
    _description = 'Weight Shift'

    name = fields.Char()
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company
    )
    hour_from = fields.Float(
        required=True,
        tracking=True
    )
    hour_to = fields.Float(
        required=True,
        tracking=True
    )
    active = fields.Boolean(
        default=True
    )
