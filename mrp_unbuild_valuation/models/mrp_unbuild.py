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

    def action_unbuild(self):
        res = super().action_unbuild()
        self._update_stock_valuation_layer_ids()
        return res

    def _update_stock_valuation_layer_ids(self):
        """
        This method should be overriden if new methods are added
        via inheritance
        """
        for unbuild in self.filtered(
            lambda x: x.valuation_method == "product_cost"
        ):
            # TODO we've already detected that all moves are produce_line_ids,
            # but this code (merging them and select them with _is_in and
            # _is_out methods) is more secure
            move_ids = (unbuild.consume_line_ids + unbuild.produce_line_ids)
            # TODO prevent more than one output move (or valuation layer)
            out_unit_cost = move_ids.filtered(
                lambda x: x._is_out()
            ).stock_valuation_layer_ids.unit_cost

            for layer in move_ids.filtered(
                lambda x: x._is_in()
            ).stock_valuation_layer_ids:
                layer.write({
                    "unit_cost": out_unit_cost,
                    "value": out_unit_cost * layer.quantity,
                })
        # Default does not change anything

    def action_view_stock_valuation_layers(self):
        self.ensure_one()
        move_ids = (self.consume_line_ids + self.produce_line_ids)
        domain = [("id", "in", move_ids.stock_valuation_layer_ids.ids)]
        action = self.env.ref(
            "stock_account.stock_valuation_layer_action"
        ).read()[0]
        action["domain"] = domain
        return action
