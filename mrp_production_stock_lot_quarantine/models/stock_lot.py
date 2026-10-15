# Copyright 2026 Solvos Consultoría Informática, S.L. (<https://www.solvos.es>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import models


class StockLot(models.Model):
    _inherit = "stock.lot"

    def _inherit_purification_state(self, source_lots):
        self.ensure_one()
        blocked_sources = source_lots.filtered(
            lambda lot: lot.purification_state == "blocked"
            and lot.purification_release_date
        )
        if not blocked_sources:
            self._mark_exempt()
            return

        latest_start_date = max(
            blocked_sources.mapped("purification_start_date")
        )
        inherited_hours = (
            max(blocked_sources.mapped("purification_release_date"))
            - latest_start_date
        ).total_seconds() / 3600.0

        self.write(
            {
                "purification_state": "blocked",
                "purification_start_date": latest_start_date,
                "purification_hours": inherited_hours,
            }
        )
