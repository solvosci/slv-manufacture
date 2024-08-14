# © 2024 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3.0 (https://www.gnu.org/licenses/agpl-3.0.html)

from odoo import fields, models, _


class MrpIncidenceType(models.Model):
    _name = "mrp.incidence.type"
    _description = 'mrp.incidence.type'

    name = fields.Char(required=True)
    code = fields.Char()
    incidence_ids = fields.One2many('mrp.unbuild.incidence', 'incidence_type_id')
    incidence_count = fields.Integer(compute='_compute_incidence_count')
    active = fields.Boolean(default=True)

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

    def write(self, vals):
        if 'active' in vals:
            # TODO: Refactor this method when creating the field related to descriptions "incidence_description_ids"
            # archiving/unarchiving a type does it on its description, too
            description_ids = self.env['mrp.incidence.description'].with_context(active_test=False).search([("incidence_type_id", "in", self.ids)])
            description_ids.write({'active': vals['active']})
        return super().write(vals)
