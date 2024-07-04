# © 2022 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See https://www.gnu.org/licenses/lgpl-3.0.html

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ManufactureOrder(models.Model):
    _inherit = "mrp.production"

    project_sequence = fields.Integer(string='Sequence')
    project_id = fields.Many2one('project.project')

    @api.onchange("project_id")
    def _onchange_project_id(self):
        if not self.project_id:
            self.project_sequence = 0

