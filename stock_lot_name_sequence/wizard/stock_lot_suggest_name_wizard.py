# Copyright 2026 Solvos Consultoría Informática, S.L. (<https://www.solvos.es>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class StockLotSuggestNameWizard(models.TransientModel):
    _name = "stock.lot.suggest.name.wizard"
    _description = "Suggest Lot/Serial Name"

    lot_id = fields.Many2one("stock.lot", required=True, readonly=True)
    product_id = fields.Many2one(related="lot_id.product_id", readonly=True)
    current_name = fields.Char(related="lot_id.name", readonly=True)
    suggested_name = fields.Char(compute="_compute_suggested_name", store=True, readonly=False)

    @api.depends("lot_id")
    def _compute_suggested_name(self):
        for wizard in self:
            wizard.suggested_name = wizard.lot_id._suggest_name(
                wizard.lot_id.product_id, wizard.lot_id.company_id
            )

    def button_confirm(self):
        self.ensure_one()
        self.lot_id.name = self.suggested_name
        return False
