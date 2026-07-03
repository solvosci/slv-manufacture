# © 2026 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See https://www.gnu.org/licenses/lgpl-3.0.html

from odoo import api, SUPERUSER_ID


def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    workorders = env["mrp.workorder"].search(
        [
            ("date_planned_start", "!=", False),
            ("date_first_scheduled_start", "=", False),
        ]
    )
    for wo in workorders:
        wo.write(
            {
                "date_first_scheduled_start": wo.date_planned_start,
                "date_first_scheduled_finished": wo.date_planned_finished,
            }
        )
