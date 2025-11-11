# © 2025 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See https://www.gnu.org/licenses/lgpl-3.0.html

from odoo import fields, models


class ManufactureOrder(models.Model):
    _inherit = 'mrp.production'

    wp_timesheet_ids = fields.One2many('account.analytic.line', 'mrp_production_id')
    wp_timesheet_count = fields.Integer(compute='_compute_wp_timesheet_count')

    def _compute_wp_timesheet_count(self):
        for record in self:
            record.wp_timesheet_count = len(record.wp_timesheet_ids)

    def write(self, vals):
        res = super(ManufactureOrder, self).write(vals)
        if 'project_id' in vals:
            self.wp_timesheet_ids.with_context(allow_mrp_timesheet=True).write({
                'project_id': self.project_id.id
            })
        return res
