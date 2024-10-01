# © 2024 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (https://www.gnu.org/licenses/lgpl-3.0.html)

from odoo import api, models, fields
from odoo.tools.float_utils import float_compare


class MrpUnbuild(models.Model):
    _inherit = "mrp.unbuild"

    # TODO it's not computed because user can change base date before
    #      unbuild is done, so we should store it when unbuild is done
    shift_effective_time = fields.Float(
        readonly=True,
    )

    currency_id = fields.Many2one(related="company_id.currency_id")
    cost_extra_waste = fields.Monetary(
        string="Unbuild extra cost - waste",
        readonly=True,
        copy=False,
    )
    cost_extra_waste_unit = fields.Monetary(
        compute="_compute_cost_unitary_fields",
        string="Unbuild extra cost - waste (unitary)",
    )
    cost_extra_pt_manpower = fields.Monetary(
        string="Unbuild extra cost - process type (manpower)",
        readonly=True,
        copy=False,
    )
    cost_extra_pt_manpower_unit = fields.Monetary(
        compute="_compute_cost_unitary_fields",
        string="Unbuild extra cost - process type (manpower) (unitary)",
    )
    cost_extra_pt_energy = fields.Monetary(
        string="Unbuild extra cost - process type (energy)",
        readonly=True,
        copy=False,
    )
    cost_extra_pt_energy_unit = fields.Monetary(
        compute="_compute_cost_unitary_fields",
        string="Unbuild extra cost - process type (energy) (unitary)",
    )
    cost_extra_pt_amortization = fields.Monetary(
        string="Unbuild extra cost - process type (amortization)",
        readonly=True,
        copy=False,
    )
    cost_extra_pt_amortization_unit = fields.Monetary(
        compute="_compute_cost_unitary_fields",
        string="Unbuild extra cost - process type (amortization) (unitary)",
    )
    cost_extra_pt_repair_maintenance_mgmt = fields.Monetary(
        string="Unbuild extra cost - process type (Repair/Maintenance management)",
        readonly=True,
        copy=False,
    )
    cost_extra_pt_repair_maintenance_mgmt_unit = fields.Monetary(
        compute="_compute_cost_unitary_fields",
        string="Unbuild extra cost - process type (Repair/Maintenance management) (unitary)",
    )
    cost_extra_pt_consumable = fields.Monetary(
        string="Unbuild extra cost - process type (consumables)",
        readonly=True,
        copy=False,
    )
    cost_extra_pt_consumable_unit = fields.Monetary(
        compute="_compute_cost_unitary_fields",
        string="Unbuild extra cost - process type (consumables) (unitary)",
    )
    cost_extra_pt_maquila = fields.Monetary(
        string="Unbuild extra cost - process type (maquilas)",
        readonly=True,
        copy=False,
    )
    cost_extra_pt_maquila_unit = fields.Monetary(
        compute="_compute_cost_unitary_fields",
        string="Unbuild extra cost - process type (maquilas) (unitary)",
    )
    cost_extra_process_type = fields.Monetary(
        string="Unbuild extra cost - process type",
        readonly=True,
        copy=False,
    )
    cost_extra_process_type_unit = fields.Monetary(
        compute="_compute_cost_unitary_fields",
        string="Unbuild extra cost - process type (unitary)",
    )
    cost_extra_total = fields.Monetary(
        string="Unbuild extra cost - total",
        readonly=True,
        copy=False,
    )
    cost_wo_extra_total = fields.Monetary(
        string="Unbuild w/o extra cost - total",
        readonly=True,
        copy=False,
    )
    cost_wo_extra_total_unit = fields.Monetary(
        compute="_compute_cost_unitary_fields",
        string="Unbuild w/o extra cost - total (unitary)",
    )
    cost_product_qty = fields.Float(
        string="Components cost product quantity",
        readonly=True,
        copy=False,
    )
    cost_product_perf = fields.Float(
        string="Costs Unbuild Performance",
        compute="_compute_cost_product_perf",
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
        # TODO set other cost_extra_process_type and cost_extra_pt_* to 0.0
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
        self.shift_effective_time = self._get_shift_effective_time()
        self._set_cost_extra_process_type()

        # e.g. 120 €
        self.cost_extra_total = (
            self.cost_extra_waste + self.cost_extra_process_type
        )

        self.cost_product_qty = self._get_cost_product_qty()

        # PHAP_sudo = self.env["product.history.average.price"]
        # # TODO pending unbuild_date must be filled. Replaces
        # #      stock_move_action_done_custdate in mrp_unbuild_advanced passing date mechanism
        # # e.g. 250 €/t
        # product_price = PHAP_sudo.get_price(
        #     self.product_id,
        #     self.location_id.get_warehouse(),
        #     dt=self.unbuild_date
        # )
        # # e.g. (250 €/t) * 3 t = 750,00 €
        # self.cost_wo_extra_total = product_price * self.product_qty
        self._update_wo_extra_total()

    def _update_wo_extra_total(self):
        self.ensure_one()
        # TODO si sudo() finally required
        PHAP_sudo = self.env["product.history.average.price"]
        product_price = PHAP_sudo.get_price(
            self.product_id,
            self.location_id.get_warehouse(),
            dt=self.unbuild_date
        )
        # e.g. (250 €/t) * 3 t = 750,00 €
        self.cost_wo_extra_total = product_price * self.product_qty

    def _compute_cost_product_perf(self):
        mrp_perf = self.filtered(
            lambda x: float_compare(
                x.product_qty,
                0.0,
                precision_rounding=x.product_uom_id.rounding or 0.001
            ) == 1
        )
        for mrp in mrp_perf:
            mrp.cost_product_perf = (
                mrp.cost_product_qty / mrp.product_qty
            )
        (self - mrp_perf).write({"cost_product_perf": 0.0})

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

    def _compute_cost_unitary_fields(self):
        mrp_unitary = self.filtered(
            lambda x: float_compare(
                x.cost_product_qty,
                0.0,
                precision_rounding=x.product_uom_id.rounding or 0.001
            ) == 1
        )
        for mrp in mrp_unitary:
            qty = mrp.cost_product_qty
            mrp.write({
                "cost_wo_extra_total_unit": mrp.cost_wo_extra_total / qty,
                "cost_extra_waste_unit": mrp.cost_extra_waste / qty,
                "cost_extra_process_type_unit": mrp.cost_extra_process_type / qty,
                "cost_extra_pt_manpower_unit": mrp.cost_extra_pt_manpower / qty,
                "cost_extra_pt_energy_unit": mrp.cost_extra_pt_energy / qty,
                "cost_extra_pt_amortization_unit": mrp.cost_extra_pt_amortization / qty,
                "cost_extra_pt_repair_maintenance_mgmt_unit": mrp.cost_extra_pt_repair_maintenance_mgmt / qty,
                "cost_extra_pt_consumable_unit": mrp.cost_extra_pt_consumable / qty,
                "cost_extra_pt_maquila_unit": mrp.cost_extra_pt_maquila / qty,
            })
        (self - mrp_unitary).write({
            "cost_wo_extra_total_unit": 0.0,
            "cost_extra_waste_unit": 0.0,
            "cost_extra_process_type_unit": 0.0,
            "cost_extra_pt_manpower_unit": 0.0,
            "cost_extra_pt_energy_unit": 0.0,
            "cost_extra_pt_amortization_unit": 0.0,
            "cost_extra_pt_repair_maintenance_mgmt_unit": 0.0,
            "cost_extra_pt_consumable_unit": 0.0,
            "cost_extra_pt_maquila_unit": 0.0,
        })

    def _get_cost_extra_waste(self):
        self.ensure_one()
        cost_waste = 0.0
        for total in self.bom_quants_total_ids.filtered(
            lambda x: x.bom_line_id.product_id.has_waste_cost_mgmt
        ):
            product = total.bom_line_id.product_id
            pricelist = product.waste_mgmt_pricelist_id
            price = 0.0
            total_qty = total.product_uom_id._compute_quantity(
                total.total_qty, product.uom_id
            )
            if pricelist:
                price, rule_id = pricelist.get_product_price_rule(
                    product, total_qty, False, date=self.unbuild_date
                )
            cost_waste += total_qty * price
        return cost_waste

    def _get_shift_effective_time(self):
        self.ensure_one()
        return (
            self.shift_total_time - self.shift_break_time - self.shift_stop_time
        )

    def _set_cost_extra_process_type(self):
        self.ensure_one()
        if not self.process_type_id:
            # TODO set other cost_extra_pt_* to 0.0
            self.cost_extra_process_type = 0.0
        self.write(self.process_type_id._get_costs(self))

    def _get_cost_product_qty(self):
        self.ensure_one()
        # TODO disabled_mrp_unbuild_valuation inherited mark instead of BoM mark
        quant_totals_ids = self.bom_quants_total_ids.filtered(lambda x: (
            not x.bom_line_id.product_id.has_waste_cost_mgmt
            # and not x.bom_line_id.disabled_mrp_unbuild_valuation
            and not x.disabled_mrp_unbuild_valuation
        ))
        return sum(
            qt.product_uom_id._compute_quantity(
                qt.total_qty, self.product_uom_id
            )
            for qt in quant_totals_ids
        )
