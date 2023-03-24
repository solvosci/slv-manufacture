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

    @api.constrains("project_id", "project_sequence")
    def _check_project_values(self):
        self.ensure_one()
        if self.project_id and self.project_sequence <= 0:
            raise ValidationError(_('Sequence code is mandatory.\nPlease write a code greater than 0'))
        if self.project_id.manufacture_ids.filtered(
            lambda x: x.project_sequence == self.project_sequence
            and x.id != self.id
        ):
            raise ValidationError(_('The manufacture order with same project sequence already exists in the project'))
