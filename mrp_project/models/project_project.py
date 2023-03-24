# © 2022 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See https://www.gnu.org/licenses/lgpl-3.0.html

from odoo import api, models, fields, _

class ProjectProject(models.Model):
    _inherit = "project.project"

    manufacture_ids = fields.One2many('mrp.production', 'project_id')
    manufacture_order_count = fields.Integer(compute='_compute_manufacture_order_count')

    def _compute_manufacture_order_count(self):
        for record in self:
            record.manufacture_order_count = len(record.manufacture_ids)

    def binded_productions(self):
        self.ensure_one()
        domain = [('project_id', '=', self.id)]
        return {
            'name': _('Related Manufactures'),
            'domain': domain,
            'res_model': 'mrp.production',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'kanban,tree,form',
            'view_type': 'form',
            'context': "{'default_project_id': %s, 'manufacture_binding_list': %s}" % (self.id, True)
        }
