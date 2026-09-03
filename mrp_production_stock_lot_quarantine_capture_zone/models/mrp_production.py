# Copyright 2026 Solvos Consultoría Informática, S.L. (<https://www.solvos.es>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import _, models
from odoo.fields import Command


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    def _post_inventory(self, cancel_backorder=False):
        res = super()._post_inventory(cancel_backorder=cancel_backorder)
        for production in self:
            production._propagate_capture_origin_to_finished_lots()
        return res

    def _propagate_capture_origin_to_finished_lots(self):
        self.ensure_one()
        component_origins = self.move_raw_ids.mapped(
            "move_line_ids.lot_id.capture_origin_ids"
        )
        if not component_origins:
            return

        finished_lots = self.move_finished_ids.mapped("move_line_ids.lot_id")
        if not finished_lots:
            return

        component_types = component_origins.product_type_id
        new_origin_vals = []
        for finished_lot in finished_lots:
            product = finished_lot.product_id
            missing_types = component_types - product.intecmar_categ
            if missing_types:
                product.sudo().intecmar_categ = [Command.link(t.id) for t in missing_types]
                self.message_post(body=_(
                    "Product %(product)s was missing INTECMAR product "
                    "type(s), present in its consumed "
                    "components added automatically so the toxin "
                    "block could be evaluated.",
                    product=product.display_name,
                ))
            new_origin_vals += [
                {
                    "lot_id": finished_lot.id,
                    "capture_zone_id": origin.capture_zone_id.id,
                    "product_type_id": origin.product_type_id.id,
                    "capture_date": origin.capture_date,
                }
                for origin in component_origins
            ]
        self.env["lot.capture.zone.origin"].sudo().create(new_origin_vals)
        finished_lots._evaluate_toxin_block()
