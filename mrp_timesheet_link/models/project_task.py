# © 2023 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html

from odoo import models, fields, _


class ProjectTask(models.Model):
    _inherit = "project.task"

    production_id = fields.Many2one('mrp.production', readonly=True, copy=False)
