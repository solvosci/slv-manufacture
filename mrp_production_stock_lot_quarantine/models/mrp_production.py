# Copyright 2026 Solvos Consultoría Informática, S.L. (<https://www.solvos.es>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import _, fields, models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    restart_purification = fields.Boolean(
        string="Restart Purification Process",
        default=False,
        help="Check to treat the resulting lot(s) as freshly received.",
    )

    def _post_inventory(self, cancel_backorder=False):
        res = super()._post_inventory(cancel_backorder=cancel_backorder)
        for production in self:
            production._propagate_purification_to_finished_lots()
        return res

    def _propagate_purification_to_finished_lots(self):
        self.ensure_one()
        finished_move_lines = self.move_finished_ids.mapped("move_line_ids")
        if not finished_move_lines:
            return

        for finished_lot in finished_move_lines.mapped("lot_id").filtered(
            lambda l: l.product_id.purifiable
        ):
            if self.restart_purification:
                finished_lot._start_quarantine(
                    finished_lot.product_id.purification_hours
                )
            else:
                finished_lot._inherit_purification_state(
                    self.move_raw_ids.mapped("move_line_ids.lot_id")
                )
            if (
                finished_lot.purification_state == "blocked"
                and not self.picking_type_id.warehouse_id.quarantine_location_id
            ):
                self.message_post(
                    body=_(
                        "Reclassified lot is blocked but this "
                        "warehouse has no Quarantine Location configured."
                    )
                )
