# © 2024 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3.0 (https://www.gnu.org/licenses/agpl-3.0.html)

from odoo import fields, models, _

class MrpIncidenceType(models.Model):
    _name = "mrp.incidence.type"
    _description = 'mrp.incidence.type'

    name = fields.Char()
    code = fields.Char()
    incidence_ids = fields.One2many('mrp.unbuild.incidence', 'incidence_type_id')
    incidence_count = fields.Integer(compute='_compute_incidence_count')

    def _compute_incidence_count(self):
        for record in self:
            record.incidence_count = len(record.incidence_ids)


    def action_view_incidence(self):
        action = {
            'name': _('Incidences'),
            'type': 'ir.actions.act_window',
            'res_model': 'mrp.unbuild.incidence',
            'target': 'current',
        }
        action['view_mode'] = 'tree'
        action['domain'] = [('id', 'in', self.incidence_ids.ids)]
        return action
