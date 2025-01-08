# © 2025 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html
from odoo import api, models


class StockMove(models.Model):
    _inherit = "stock.move"

    @api.depends("raw_material_production_id.sn_locked")
    def _compute_button_add_sn_invisible(self):
        super()._compute_button_add_sn_invisible()
        # TODO this should be another mark in the future
        self.filtered(
            lambda x: not x.button_add_sn_invisible
            and x.raw_material_production_id
            and x.raw_material_production_id.sn_locked
        ).update({"button_add_sn_invisible": True})

    def sn_should_be_readonly(self):
        ret = super().sn_should_be_readonly()
        return bool(self.raw_material_production_id) or ret
