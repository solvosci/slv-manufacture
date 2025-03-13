# © 2025 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (https://www.gnu.org/licenses/lgpl-3.0.html)

from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _mrp_unlink_previous_stuff(self):
        super()._mrp_unlink_previous_stuff()
        self._unlink_previous_stuff()
