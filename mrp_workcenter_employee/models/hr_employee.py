# © 2026 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html

from odoo import models, fields


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    workcenter_ids = fields.Many2many(
        "mrp.workcenter",
        string="Work Centers",
        help="Work centers where this employee can work.",
    )

    workorder_ids = fields.One2many(
        "mrp.workorder",
        "employee_id",
        string="Work Orders",
    )

    def _get_scheduled_hours(self, date_from, date_to):
        """Hours the employee is scheduled to work between two datetimes.
        Extension point: leaves are not discounted here (compute_leaves=False).
        """
        self.ensure_one()
        calendar = self.resource_calendar_id
        if not calendar:
            return 0.0
        return calendar.get_work_hours_count(date_from, date_to, compute_leaves=False)
