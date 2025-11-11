# © 2025 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See https://www.gnu.org/licenses/lgpl-3.0.html

from odoo import fields, models, _
from odoo.exceptions import UserError


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    mrp_production_id = fields.Many2one('mrp.production', copy=False)
    mrp_workorder_id = fields.Many2one('mrp.workorder', ondelete='cascade', copy=False)
    mrp_workcenter_productivity_ids = fields.Many2many('mrp.workcenter.productivity', ondelete='cascade', copy=False)

    def restriction_allow_mrp_timesheet(self):
        if self.mrp_workcenter_productivity_ids and not self.env.context.get('allow_mrp_timesheet'):
            raise UserError(_('You do not have permission to edit/delete a timesheet related to manufacturing.'))

    def write(self, values):
        res = super(AccountAnalyticLine, self).write(values)
        self.restriction_allow_mrp_timesheet()
        return res

    def unlink(self):
        self.restriction_allow_mrp_timesheet()
        return super(AccountAnalyticLine, self).unlink()
