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

    def _assign_project_to_children(self):
        self.ensure_one()
        child_mrp = self._get_children()
        for child in child_mrp:
            child.project_id = self.project_id
            child._assign_project_to_children()

    @api.onchange("project_id")
    def _onchange_project_id_parent(self):
        self._assign_project_to_children()

    @api.model
    def create(self, values):
        # This part of the code is triggered by another automated process and is executed by OdooBot with permissions
        production = super().create(values)
        production_source = production._get_sources()
        if production_source and len(production_source) == 1:
            production.project_id = production_source.project_id
        return production
