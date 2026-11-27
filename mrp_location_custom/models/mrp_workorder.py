# Copyright 2026 Solvos Consultoría Informática
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class MrpWorkorder(models.Model):
    _inherit = 'mrp.workorder'

    def button_start(self):
        self.ensure_one()
        # This check is to allow MOs without custom routes to start workorders without any issues.
        # Also that MOs that are in progress and haven't been assigned a custom route because
        # the adddon was installed after the MO was created, can also start workorders without any issues.
        if self.production_id.custom_route_id:
            self.production_id._check_workorders_can_start()
        return super().button_start()
