# © 2022 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html

from odoo import models, fields, _

class ResCompany(models.Model):
    _inherit = 'res.company'

    weight_scale_username_id = fields.Many2one('res.users',string='Username')
    weight_scale_password = fields.Char(string='Password')
    weight_scale_limit = fields.Float(string='Maximum kg limit on weight scale', default=200)
