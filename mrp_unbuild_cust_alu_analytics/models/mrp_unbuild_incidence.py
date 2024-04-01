# © 2024 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (https://www.gnu.org/licenses/lgpl-3.0.html)

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class MrpUnbuildIncidence(models.Model):
    _name = "mrp.unbuild.incidence"
    _description = 'MRP Incidence'

    code = fields.Char(required=True)
    description = fields.Char(required=True)
    duration = fields.Float(required=True)
    machine = fields.Char()
    criticallity = fields.Selection([
        ('high','High'),
        ('medium','Medium'),
        ('low','Low'),
    ])
    stage = fields.Selection([
        ('in_progress','In progress'),
        ('solved','Solved')
    ])
    priority = fields.Selection([
        ('high','High'),
        ('medium','Medium'),
        ('low','Low'),
    ])
    unbuild_id = fields.Many2one(
        comodel_name="mrp.unbuild",
    )
