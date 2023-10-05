# © 2023 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class MRPProduction(models.Model):
    _inherit = 'mrp.production'

    project_id = fields.Many2one(
        comodel_name='project.project',
        domain=[("allow_timesheets", "=", True)],
        copy=False,
    )
    task_id = fields.Many2one(comodel_name='project.task', copy=False)

    timesheet_count = fields.Integer(compute='_compute_timesheet_count')

    @api.onchange('project_id')
    def _onchange_project_id(self):
        self.task_id.production_id = False
        self.task_id = False

    def _compute_timesheet_count(self):
        for record in self:
            record.timesheet_count = len(record.task_id.timesheet_ids)

    def write(self, vals):
        if vals.get('task_id'):
            if len(self) > 1:
                raise ValidationError(_(
                    "Cannot set the same task for more than one production"
                ))
            self.task_id.production_id = False
            self.env['project.task'].browse(vals["task_id"]).production_id = self
        return super(MRPProduction, self).write(vals)

    def action_view_timesheets(self):
        action = {
            'name': _('Timesheet'),
            'view_mode': 'tree,form',
            'res_model': 'account.analytic.line',
            'type': 'ir.actions.act_window',
            'domain': [('task_id.production_id', '=', self.id)]
        }
        return action

    def action_cancel(self):
        res = super(MRPProduction, self).action_cancel()
        if self.task_id:
            self.project_id = False
            self.task_id.production_id = False
            self.task_id = False
        return res
