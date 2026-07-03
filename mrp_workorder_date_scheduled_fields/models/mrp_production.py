# © 2026 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See https://www.gnu.org/licenses/lgpl-3.0.html

from odoo import models

class MrpProduction(models.Model):
    _inherit = "mrp.production"

    def _plan_workorders(self, replan=False):
        res = super()._plan_workorders(replan=replan)
        for wo in self.workorder_ids.filtered(
            lambda w: not w.date_first_scheduled_start
            and w.date_planned_start
        ):
            wo.write(
                {
                    "date_first_scheduled_start": wo.date_planned_start,
                    "date_first_scheduled_finished": wo.date_planned_finished,
                }
            )
        return res
