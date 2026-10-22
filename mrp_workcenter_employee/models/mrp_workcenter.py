# © 2026 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html
from odoo import models, fields, api
from datetime import datetime, time, timedelta


class MrpWorkcenter(models.Model):
    _inherit = "mrp.workcenter"

    employee_ids = fields.Many2many(
        "hr.employee",
        string="Employees",
        help="Employees who work in this work center."
        "This field is used to filter the employees available for the work orders of this work center.",
    )
    week_date = fields.Date(
        string="Reference Date",
        compute="_compute_week_date",
        inverse="_inverse_week_date",
        help="Any date of the week to show. Defaults to today.",
    )
    week_start = fields.Date(compute="_compute_current_week_load")
    week_end = fields.Date(compute="_compute_current_week_load")
    week_capacity_hours = fields.Float(
        string="Week Capacity (h)",
        compute="_compute_current_week_load",
        help="Scheduled hours of the employees of this work center in the week.",
    )
    week_planned_hours = fields.Float(
        string="Week Planned (h)",
        compute="_compute_current_week_load",
        help="Expected duration of the work orders starting in the week.",
    )
    week_available_hours = fields.Float(
        string="Week Available (h)", compute="_compute_current_week_load"
    )
    week_load_label = fields.Char(
        string="Week Load",
        compute="_compute_current_week_load",
        help="Available hours / capacity hours, as HH:MM.",
    )

    # ---- Selected week
    def _compute_week_date(self):
        today = fields.Date.context_today(self)
        for workcenter in self:
            workcenter.week_date = today

    def _inverse_week_date(self):
        """Nothing to store: the selected date only drives the computation."""

    def write(self, vals):
        # The reference date only drives the computation: writing just that
        # field must not touch the record (nor its write_date/write_uid).
        if set(vals) == {"week_date"}:
            return True
        return super().write(vals)

    # ---- Week helpers
    @api.model
    def _get_week_bounds(self, date=None):
        """Return the [start, end) datetimes of the Monday-based week of date."""
        date = fields.Date.to_date(date) or fields.Date.context_today(self)
        week_start = datetime.combine(date - timedelta(days=date.weekday()), time.min)
        return week_start, week_start + timedelta(days=7)

    @api.model
    def _format_hours(self, hours):
        """Format a float number of hours as HH:MM (negative values keep the sign)."""
        total_minutes = round(abs(hours) * 60)
        sign = "-" if hours < 0 and total_minutes else ""
        return "%s%02d:%02d" % (sign, *divmod(total_minutes, 60))

    def _get_week_workorder_domain(self, week_start, week_end):
        return [
            ("workcenter_id", "in", self.ids),
            ("state", "!=", "cancel"),
            ("date_planned_start", ">=", week_start),
            ("date_planned_start", "<", week_end),
        ]

    # ---- Capacity and load
    def _get_week_capacity_hours(self, week_start, week_end):
        self.ensure_one()
        return sum(
            employee._get_scheduled_hours(week_start, week_end)
            for employee in self.employee_ids
        )

    def _get_week_planned_hours(self, week_start, week_end):
        """Return {workcenter id: planned hours}; duration_expected is in minutes."""
        groups = self.env["mrp.workorder"].read_group(
            self._get_week_workorder_domain(week_start, week_end),
            ["duration_expected:sum"],
            ["workcenter_id"],
        )
        return {
            group["workcenter_id"][0]: group["duration_expected"] / 60.0
            for group in groups
        }

    def _get_week_load(self, date=None):
        """Return {workcenter id: {capacity_hours, planned_hours, available_hours}}."""
        week_start, week_end = self._get_week_bounds(date)
        planned = self._get_week_planned_hours(week_start, week_end)
        result = {}
        for workcenter in self:
            capacity = workcenter._get_week_capacity_hours(week_start, week_end)
            # _origin: while editing a form the record has a temporary id
            planned_hours = planned.get(workcenter._origin.id, 0.0)
            result[workcenter.id] = {
                "capacity_hours": capacity,
                "planned_hours": planned_hours,
                "available_hours": capacity - planned_hours,
            }
        return result

    @api.model
    def get_week_load(self, date=None, workcenter_ids=None):
        """Public method for the views: load of the week of ``date``."""
        workcenters = self.browse(workcenter_ids) if workcenter_ids else self.search([])
        week_start, _week_end = self._get_week_bounds(date)
        return [
            dict(
                vals,
                workcenter_id=workcenter_id,
                week_start=fields.Datetime.to_string(week_start),
            )
            for workcenter_id, vals in workcenters._get_week_load(date).items()
        ]

    @api.depends(
        "week_date",
        "employee_ids",
        "employee_ids.resource_calendar_id",
        "order_ids.duration_expected",
        "order_ids.date_planned_start",
        "order_ids.state",
    )
    def _compute_current_week_load(self):
        for week_date in set(self.mapped("week_date")):
            workcenters = self.filtered(lambda wc: wc.week_date == week_date)
            week_start, week_end = self._get_week_bounds(week_date)
            load = workcenters._get_week_load(week_date)
            for workcenter in workcenters:
                vals = load[workcenter.id]
                workcenter.week_start = week_start.date()
                workcenter.week_end = (week_end - timedelta(days=1)).date()
                workcenter.week_capacity_hours = vals["capacity_hours"]
                workcenter.week_planned_hours = vals["planned_hours"]
                workcenter.week_available_hours = vals["available_hours"]
                workcenter.week_load_label = "%s/%s" % (
                    self._format_hours(vals["available_hours"]),
                    self._format_hours(vals["capacity_hours"]),
                )
