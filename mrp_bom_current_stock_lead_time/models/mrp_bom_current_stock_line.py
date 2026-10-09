# © 2026 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3.0 - See (https://www.gnu.org/licenses/agpl-3.0).
from odoo import api, fields, models
from odoo.tools import float_compare


class BomRouteCurrentStockLine(models.TransientModel):
    _inherit = "mrp.bom.current.stock.line"

    supply_type = fields.Selection(
        [("manufacture", "Manufacture"), ("buy", "Buy"), ("none", "No Supply Data")],
        string="Supply",
        compute="_compute_supply",
    )
    needs_supply = fields.Boolean(compute="_compute_supply")
    lead_time_days = fields.Float(
        string="Lead Time (days)",
        compute="_compute_supply",
        help="Zero if the stock in the source location covers the need.",
    )

    @api.depends(
        "product_id", "product_qty", "product_uom_id", "qty_available_in_source_loc"
    )
    def _compute_supply(self):
        for line in self:
            supply_type = line._get_supply_type()
            line.supply_type = supply_type
            line.needs_supply = line._get_needs_supply()
            line.lead_time_days = (
                line._get_lead_time(supply_type) if line.needs_supply else 0.0
            )

    def _get_needs_supply(self):
        self.ensure_one()
        return (
            float_compare(
                self.qty_available_in_source_loc,
                self.product_qty,
                precision_rounding=self.product_uom_id.rounding,
            )
            < 0
        )

    def _get_supply_type(self):
        self.ensure_one()
        if self.product_id.bom_ids:
            return "manufacture"
        return "buy" if self.product_id.seller_ids else "none"

    def _get_lead_time(self, supply_type):
        self.ensure_one()
        product = self.product_id
        if supply_type == "manufacture":
            return product.produce_delay
        if supply_type == "buy":
            seller = (
                product._select_seller(
                    quantity=self.product_qty, uom_id=self.product_uom_id
                )
                or product.seller_ids[:1]
            )
            return seller.delay
        return 0.0