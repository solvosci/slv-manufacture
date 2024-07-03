# © 2024 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (https://www.gnu.org/licenses/lgpl-3.0.html)

from odoo import api, models, fields


class MrpUnbuild(models.Model):
    _inherit = "mrp.unbuild"

    currency_id = fields.Many2one(related="company_id.currency_id")
    cost_extra_waste = fields.Monetary(
        string="Unbuild extra cost - waste",
        readonly=True,
    )
    cost_extra_total = fields.Monetary(
        string="Unbuild extra cost - total",
        readonly=True,
    )
    cost_wo_extra_total = fields.Monetary(
        string="Unbuild w/o extra cost - total",
        readonly=True,
    )
    cost_product_qty = fields.Float(
        string="Components cost product quantity",
        readonly=True,
    )
    cost_unit_price = fields.Monetary(
        compute="_compute_cost_fields",
        string="Components unit cost price",
        compute_sudo=True,
    )
    cost_total = fields.Monetary(
        compute="_compute_cost_fields",
        string="Unbuild total cost",
        compute_sudo=True,
    )

    def action_unbuild(self):
        self.sudo()._save_cost_fields()
        return super().action_unbuild()
    
    def action_back_draft(self):
        self.write({
            "cost_extra_waste": 0.0,
            "cost_extra_total": 0.0,
            "cost_wo_extra_total": 0.0,
            "cost_product_qty": 0.0,
        })
        super().action_back_draft()

    def _save_cost_fields(self):
        if not self.product_qty:
            return
        self.cost_extra_waste = self._get_cost_extra_waste()
        # e.g. 120 €
        self.cost_extra_total = (
            self.cost_extra_waste + self._get_cost_extra_others()
        )

        PHAP_sudo = self.env["product.history.average.price"]
        # TODO pending unbuild_date must be filled. Replaces
        #      stock_move_action_done_custdate in mrp_unbuild_advanced passing date mechanism
        # e.g. 250 €/t
        product_price = PHAP_sudo.get_price(
            self.product_id,
            self.location_id.get_warehouse(),
            dt=self.unbuild_date
        )
        self.cost_product_qty = self._get_cost_product_qty()
        # e.g. (250 €/t) * 3 t = 750,00 €
        self.cost_wo_extra_total = product_price * self.cost_product_qty
        # # e.g. 750 +  120 = 870,00 €
        # total_cost = self.cost_wo_extra_total + self.cost_extra_total
        # # e.g. 870,00 € / 3 t = 290,00 €/t
        # unit_cost = total_cost / self.product_qty
        # self.write({
        #     "cost_unit_price": unit_cost,
        #     "cost_extra": self.cost_extra_total,
        #     "cost_total": total_cost,
        # })
        # (self - unbuild_cost).write({
        #     "cost_unit_price": 0.0,
        #     "cost_extra": 0.0,
        #     "cost_total": 0.0,
        # })

    @api.depends("cost_product_qty", "cost_wo_extra_total", "cost_extra_total")
    def _compute_cost_fields(self):
        unbuild_cost = self.filtered(lambda x: x.product_qty)
        for unbuild in unbuild_cost:
            # e.g. 750 +  120 = 870,00 €
            values = {
                "cost_total": unbuild.cost_wo_extra_total + unbuild.cost_extra_total
            }
            # e.g. 870,00 € / 3 t = 290,00 €/t
            values["cost_unit_price"] = (
                unbuild.cost_product_qty
                and values["cost_total"] / unbuild.cost_product_qty
                or 0.0
            )
            unbuild.write(values)
        (self - unbuild_cost).write({
            "cost_unit_price": 0.0,
            "cost_total": 0.0,
        })

    def _get_cost_extra_waste(self):
        # TODO fill cost_extra_waste
        #       => determine consume for products in waste mode, depending on their pricelist
        return 120.0

    def _get_cost_extra_others(self):
        # Overridable
        return 0.0

    def _get_cost_product_qty(self):
        # TODO overridable
        # TODO at this point, BoM-asumed
        # TODO quantity conversion to unbuild UoM
        return sum(
            self.bom_id.bom_line_ids.filtered(
                lambda x: not x.disabled_mrp_unbuild_valuation
                and not x.product_id.has_waste_cost_mgmt
            ).mapped("product_qty")
        ) * self.product_qty / self.bom_id.product_qty