# © 2025 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See https://www.gnu.org/licenses/lgpl-3.0.html

from odoo import fields, models


class MRPWorkorder(models.Model):
    _inherit = 'mrp.workorder'

    wp_timesheet_ids = fields.Many2many('account.analytic.line', compute='_compute_wp_timesheet_ids')

    def _compute_wp_timesheet_ids(self):
        for record in self:
            record.wp_timesheet_ids = record.time_ids.mapped('timesheet_id')

    def write(self, vals):
        res = super(MRPWorkorder, self).write(vals)
        for record in self:
            if record.wp_timesheet_ids and vals.get('name'):
                record.wp_timesheet_ids.with_context(allow_mrp_timesheet=True).sudo().write({
                    'name': '%s - %s' % (record.production_id.name, record.name),
                })
        return res
