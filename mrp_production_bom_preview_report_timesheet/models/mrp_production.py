# © 2023 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html

from odoo import models


class MRPProduction(models.Model):
    _inherit = 'mrp.production'

    def _compute_total_cost(self):
        super(MRPProduction, self)._compute_total_cost()
        for record in self:
            record.total_cost += self.total_task_amount()

    def total_task_amount(self):
        return sum([rec.amount for rec in self.sudo().task_id.timesheet_ids]) * -1
