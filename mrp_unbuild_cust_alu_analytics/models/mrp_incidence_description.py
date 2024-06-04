# © 2024 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3.0 (https://www.gnu.org/licenses/agpl-3.0.html)

from odoo import fields, models

class MrpIncidenceDescription(models.Model):
    _name = "mrp.incidence.description"
    _description = 'mrp.incidence.description'

    name = fields.Char()
    code = fields.Char()
    incidence_type_id = fields.Many2one(
        comodel_name="mrp.incidence.type",
        string="Incidence Type",
    )
