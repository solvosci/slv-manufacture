# © 2025 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See https://www.gnu.org/licenses/lgpl-3.0.html

from odoo import fields, models, api, _
from odoo.exceptions import UserError


class MRPWorkcenterProductivity(models.Model):
    _inherit = 'mrp.workcenter.productivity'

    timesheet_id = fields.Many2one('account.analytic.line', copy=False)

    def _check_production_project_id(self):
        if not all([production.project_id for production in self.production_id]):
            raise UserError(_('To generate the related timesheets, you need to specify the project for this manufacturing.'))

    @api.model_create_multi
    def create(self, vals_list):
        mwp_ids = super(MRPWorkcenterProductivity, self).create(vals_list)
        for record in mwp_ids.filtered(lambda x: x.date_end):
            record._check_production_project_id()
            if record.production_id.project_id and record.production_id.project_id.analytic_account_id:
                record._recalculate_timesheet(record.date_end.date())
        return mwp_ids

    def write(self, vals):
        old_dates = {record.id: {'date_end': record.date_end} for record in self}
        res = super(MRPWorkcenterProductivity, self).write(vals)
        if 'date_end' not in vals:
            return res
        self._check_production_project_id()

        for record in self.filtered(lambda x: x.date_end and x.production_id.project_id and x.production_id.project_id.analytic_account_id):
            old_date = old_dates[record.id].get('date_end')
            new_date = getattr(record, 'date_end')

            if old_date and old_date.date() != new_date.date():
                record._recalculate_timesheet(old_date.date())
            if new_date:
                record._recalculate_timesheet(new_date.date())
        return res

    def unlink(self):
        for record in self.filtered(lambda x: x.timesheet_id):
            if not self.env.user.has_group('hr_timesheet.group_hr_timesheet_approver') and record.user_id != self.env.user:
                raise UserError(_('You do not have permission to delete another user work order productivity.'))
            record.date_end = record.date_start
            if not record.timesheet_id.unit_amount:
                record.timesheet_id.with_context(allow_mrp_timesheet=True).unlink()
        super(MRPWorkcenterProductivity, self).unlink()

    def _recalculate_timesheet(self, work_date):
        same_day_times = self.workorder_id.time_ids.filtered(
            lambda x: x.user_id == self.user_id
            and x.date_end
            and x.date_end.date() == work_date
        )
        total_hours = sum(same_day_times.mapped('duration')) / 60.0

        timesheet = self.workorder_id.time_ids.sudo().timesheet_id.filtered(lambda x:
            x.user_id.id  == self.user_id.id and
            x.project_id.id == self.production_id.project_id.id and
            x.account_id.id == self.production_id.project_id.analytic_account_id.id and
            x.date == work_date and
            x.mrp_production_id.id == self.workorder_id.production_id.id)

        if timesheet:
            timesheet.with_context(allow_mrp_timesheet=True).sudo().write({
                'unit_amount': total_hours,
                'mrp_workcenter_productivity_ids': [(4, self.id)]
            })
        else:
            timesheet = self.env['account.analytic.line'].with_context(allow_mrp_timesheet=True).sudo().create({
                'name': '%s - %s' % (self.production_id.name, self.workorder_id.name),
                'unit_amount': total_hours,
                'account_id': self.production_id.project_id.analytic_account_id.id,
                'project_id': self.production_id.project_id.id,
                'user_id': self.user_id.id,
                'date': work_date,
                'mrp_production_id': self.workorder_id.production_id.id,
                'mrp_workorder_id': self.workorder_id.id,
                'mrp_workcenter_productivity_ids': [(4, self.id)],
            })

        self.timesheet_id = timesheet
        if not timesheet.unit_amount:
            timesheet.with_context(allow_mrp_timesheet=True).unlink()
