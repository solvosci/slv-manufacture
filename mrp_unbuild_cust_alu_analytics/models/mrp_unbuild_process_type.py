# © 2024 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3.0 (https://www.gnu.org/licenses/agpl-3.0.html)

from odoo import fields, models

class MrpUnbuildProcessType(models.Model):
    _name = "mrp.unbuild.process.type"
    _description = 'Unbuild Process Type'

    name = fields.Char(string='Name', required=True)
    cmplanta_id = fields.Char(string='CMPlanta ID')
    bom_line_ids = fields.One2many(
        comodel_name='mrp.bom',
        inverse_name='process_type_id',
        string='Lists of Materials'
    )
