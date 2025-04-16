# © 2024 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (https://www.gnu.org/licenses/lgpl-3.0.html)

from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    val_currency_id = fields.Many2one(
        related="company_id.currency_id",
        string="Valuation Currency",
    )

    val_cost = fields.Monetary(
        currency_field="val_currency_id",
        digits="Product Price",
        compute="_compute_val_cost",
        compute_sudo=True,
        string="Valuation Cost",
    )

    val_income = fields.Monetary(
        currency_field="val_currency_id",
        digits="Product Price",
        compute="_compute_val_income",
        compute_sudo=True,
        string="Valuation Income",
    )

    val_margin = fields.Monetary(
        currency_field="val_currency_id",
        digits="Product Price",
        compute="_compute_val_margin",
        compute_sudo=True,
        string="Valuation Margin",
    )

    val_margin_pct = fields.Float(
        compute="_compute_val_margin",
        compute_sudo=True,
        string="Valuation Margin %",
    )

    val_unbuild_ids = fields.Many2many(
        comodel_name="mrp.unbuild",
        compute="_compute_val_unbuild_ids",
        compute_sudo=True,
        string="Valuation Involved Unbuilds",
    )

    def action_view_valuation_data(self):
        self.ensure_one()
        action = self.env.ref(
            "mrp_unbuild_cust_alu_analytics_valuation.action_view_valuation_data"
        ).read()[0]
        action["res_id"] = self.id
        return action

    def _compute_val_cost(self):
        pick_out = self.filtered(
            lambda x: x.picking_type_code == "outgoing" and x.state == "done"
        )
        for picking in pick_out:
            picking.val_cost = sum(
                move._get_move_cost()
                for move in picking.move_lines
            )
        # TODO replace write() by update()
        (self - pick_out).write({
            "val_cost": 0.0,
        })
    
    def _get_compute_val_income_fields(self):
        """
        This technique prevents creating a new bridge addon for sales link
        """
        fields = []
        if "sale_id" in self:
            # sale_stock is already installed
            fields.append("move_lines.sale_line_id")
        return fields
    
    @api.depends(_get_compute_val_income_fields)
    def _compute_val_income(self):
        pick_out = self.filtered(
            lambda x: x.picking_type_code == "outgoing" and x.state == "done"
        )
        for picking in pick_out:
            # TODO proper UoM conversion
            picking.val_income = sum(
                move.product_uom_qty * move._get_move_income_price_unit()
                for move in picking.move_lines
            )
        # TODO replace write() by update()
        (self - pick_out).write({
            "val_income": 0.0,
        })

    @api.depends("val_cost", "val_income")
    def _compute_val_margin(self):
        # TODO float_is_zero or float_compare
        pick_cost = self.filtered(lambda x: x.val_cost)        
        for picking in pick_cost:
            picking.val_margin = picking.val_income - picking.val_cost
            picking.val_margin_pct = picking.val_margin / picking.val_cost
        # TODO or val_margin = val_income ?
        # TODO replace write() by update()
        (self - pick_cost).write({
            "val_margin": 0.0,
            "val_margin_pct": 0.0,
        })

    def _compute_val_unbuild_ids(self):
        pick_out = self.filtered(
            lambda x: x.picking_type_code == "outgoing" and x.state == "done"
        )
        for picking in pick_out:
            val_unbuild_ids = self.env["mrp.unbuild"]
            for ml in picking.move_line_ids.filtered(lambda x: x.state == "done"):
                val_unbuild_ids |= ml.move_id._get_move_line_cost_unbuild_ids(ml)
            picking.val_unbuild_ids = val_unbuild_ids
        (self - pick_out).write({"val_unbuild_ids": False})
