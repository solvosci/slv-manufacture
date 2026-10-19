# Copyright 2026 Solvos Consultoría Informática
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from datetime import datetime, time, timedelta
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models


class MrpWorkcenter(models.Model):
    _inherit = "mrp.workcenter"

    @api.model
    def _get_period_bounds(self, date=None, scale="week"):
        """Return the [start, end) datetimes of the day, week or month of date."""
        if scale == "day":
            delta = relativedelta(days=1)
        elif scale == "month":
            date = (fields.Date.to_date(date) or fields.Date.context_today(self)).replace(
                day=1
            )
            delta = relativedelta(months=1)
        else:
            return self._get_week_bounds(date)
        date = fields.Date.to_date(date) or fields.Date.context_today(self)
        start = datetime.combine(date, time.min)
        return start, start + delta

    @api.model
    def get_period_load(self, date=None, scale="week", workcenter_ids=None):
        """Capacity and planned hours of the day, week or month of ``date``."""
        workcenters = self.browse(workcenter_ids) if workcenter_ids else self.search([])
        start, end = self._get_period_bounds(date, scale)
        planned = workcenters._get_week_planned_hours(start, end)
        period_start = fields.Date.to_string(start.date())
        period_end = fields.Date.to_string((end - timedelta(days=1)).date())
        result = []
        for workcenter in workcenters:
            capacity = workcenter._get_week_capacity_hours(start, end)
            planned_hours = planned.get(workcenter.id, 0.0)
            available = capacity - planned_hours
            result.append(
                {
                    "workcenter_id": workcenter.id,
                    "scale": scale,
                    "period_start": period_start,
                    "period_end": period_end,
                    "capacity_hours": capacity,
                    "planned_hours": planned_hours,
                    "available_hours": available,
                    "label": "%s/%s" % (
                        self._format_hours(available),
                        self._format_hours(capacity),
                    ),
                }
            )
        return result
