# © 2026 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See https://www.gnu.org/licenses/lgpl-3.0.html

from odoo import fields, models


class MrpWorkorder(models.Model):
    _inherit = "mrp.workorder"

    date_first_scheduled_start = fields.Datetime(
        string="First Scheduled Start",
        copy=False,
        help="Planned start date set the first time this work order was scheduled.",
    )
    date_first_scheduled_finished = fields.Datetime(
        string="First Scheduled End",
        copy=False,
        help="Planned end date set the first time this work order was scheduled.",
    )
