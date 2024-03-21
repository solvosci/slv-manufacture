# © 2024 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3.0 (https://www.gnu.org/licenses/agpl-3.0.html)

from odoo import fields, models

class MrpUnbuildIncidence(models.Model):
    _name = "mrp.unbuild.incidence"
    _description = 'MRP Incidence'

    description = fields.Char()
    duration = fields.Float(required=True)
    machine = fields.Char()
    state = fields.Selection([
        ('in_progress','In progress'),
        ('solved','Solved')
    ])
    unbuild_id = fields.Many2one(
        comodel_name="mrp.unbuild",
    )
    incidence_type_id = fields.Many2one(
        comodel_name='mrp.incidence.type'
    )
    unbuild_date = fields.Datetime(
        related='unbuild_id.unbuild_date',
        store=True
    )
