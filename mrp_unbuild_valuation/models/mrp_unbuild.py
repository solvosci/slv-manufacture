# © 2021 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (https://www.gnu.org/licenses/lgpl-3.0.html)

from odoo import fields, models

VALUATION_METHODS = [
    ("default", "Default"),
    ("product_cost", "Product Cost"),
]


class MrpUnbuild(models.Model):
    _inherit = "mrp.unbuild"

    valuation_method = fields.Selection(
        selection=VALUATION_METHODS,
        help="Indicates valuation method when unbuild is done:\n\n"
        "Default - The default Odoo method\n"
        "Product Cost - Unit price for Generated Products is the same"
        " of consumed product",
        default=VALUATION_METHODS[1][0],
        required=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
      )

    def _generate_produce_moves(self):
        moves = super()._generate_produce_moves()
        if self.valuation_method == "product_cost":
            moves.write({
                "price_unit": self.product_id.standard_price,
            })
        return moves

    def action_view_stock_valuation_layers(self):
        self.ensure_one()
        move_ids = (self.consume_line_ids + self.produce_line_ids)
        domain = [("id", "in", move_ids.stock_valuation_layer_ids.ids)]
        action = self.env.ref(
            "stock_account.stock_valuation_layer_action"
        ).read()[0]
        action["domain"] = domain
        return action
