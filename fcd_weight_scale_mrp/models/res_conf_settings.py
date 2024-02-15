# © 2022 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html

from odoo import models, fields

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    weight_scale_username_id = fields.Many2one(
        "res.users",
        related='company_id.weight_scale_username_id',
        string='Username',
        readonly=False,
    )
    weight_scale_password = fields.Char(related='company_id.weight_scale_password', string="Password", readonly=False)
    weight_scale_limit = fields.Float(related='company_id.weight_scale_limit', string="Kg Limit", readonly=False)
