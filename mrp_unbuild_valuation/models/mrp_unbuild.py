# © 2021 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (https://www.gnu.org/licenses/lgpl-3.0.html)

from odoo import models


class MrpUnbuild(models.Model):
    _inherit = "mrp.unbuild"

    def action_view_stock_valuation_layers(self):
        self.ensure_one()
        move_ids = (self.consume_line_ids + self.produce_line_ids)
        domain = [("id", "in", move_ids.stock_valuation_layer_ids.ids)]
        action = self.env.ref(
            "stock_account.stock_valuation_layer_action"
        ).read()[0]
        action["domain"] = domain
        return action
