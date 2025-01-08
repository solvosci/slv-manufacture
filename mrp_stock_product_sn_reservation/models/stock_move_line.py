# © 2025 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html
from odoo import api, models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    @api.depends("move_id.raw_material_production_id.sn_locked")
    def _compute_button_exchange_lot_sn_invisible(self):
        super()._compute_button_exchange_lot_sn_invisible()
        # TODO this should be another mark in the future
        self.filtered(
            lambda x: not x.button_exchange_lot_sn_invisible
            and x.move_id.raw_material_production_id
            and x.move_id.raw_material_production_id.sn_locked
        ).update({"button_exchange_lot_sn_invisible": True})
    
    def _get_document(self):
        ret = super()._get_document()
        return (
            ret
            or self.move_id.raw_material_production_id
            or False
        )
