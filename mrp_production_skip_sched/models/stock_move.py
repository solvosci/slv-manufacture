# © 2023 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See https://www.gnu.org/licenses/lgpl-3.0.html

from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _trigger_scheduler(self):
        if self.env.context.get("skip_trigger_scheduler", False):
            return
        super()._trigger_scheduler()
