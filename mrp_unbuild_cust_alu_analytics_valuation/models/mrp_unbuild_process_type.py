# © 2024 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3.0 (https://www.gnu.org/licenses/agpl-3.0.html)

from odoo import _, api, fields, models

from datetime import timedelta

COST_UNIT_SELECTION_FIELDS = [
    ('cost_hr_manpower',_("Manpower unit cost")),
    ('cost_hr_energy', _("Energy unit cost")),
    ('cost_hr_amortization', _("Amortization unit cost")),
    ('cost_hr_repair_maintenance_mgmt', _("Repair/Maintenance management unit cost")),
    ('cost_unit_consumable', _("Consumable unit cost")),
    ('cost_unit_maquila', _("Maquila unit cost")),
]


class MrpUnbuildProcessType(models.Model):
    _inherit = "mrp.unbuild.process.type"

    cost_hr_manpower = fields.Monetary(
        "Manpower unit cost",
        currency_field='currency_id',
        tracking=True,
        default=0.0,
    )
    cost_hr_energy = fields.Monetary(
        "Energy unit cost",
        currency_field='currency_id',
        tracking=True,
        default=0.0
    )
    cost_hr_amortization = fields.Monetary(
        "Amortization unit cost",
        currency_field='currency_id',
        tracking=True,
        default=0.0
    )
    cost_hr_repair_maintenance_mgmt = fields.Monetary(
        'Repair/Maintenance management unit cost',
        currency_field='currency_id',
        tracking=True,
        default=0.0
    )
    currency_id = fields.Many2one(
        'res.currency',
        related='company_id.currency_id',
        readonly=True
    )

    cost_unit_uom_id = fields.Many2one(
        comodel_name="uom.uom",
        domain=[("measure_type", "=", "weight")],
        required=True,
        default=lambda self: self.env.ref("uom.product_uom_ton"),
        string="UoM for unit costs (by unit)",
    )
    cost_unit_consumable = fields.Monetary(
        string="Consumables unit cost (by unit)",
        tracking=True,
    )
    cost_unit_maquila = fields.Monetary(
        string="Maquilas unit cost (by unit)",
        tracking=True,
    )

    cost_pricelist_ids = fields.One2many(
        comodel_name="product.pricelist",
        inverse_name="unbuild_process_type_id",
        string="Unit Costs History",
    )

    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        res._create_costs_pricelists()
        return res
    
    def write(self, values):
        res = super().write(values)
        changed_fields = list(values.keys())
        cost_fields = self._get_costs_fields()
        changed_cost_fields = list(set(changed_fields) & set(cost_fields))
        for cost_field in changed_cost_fields:
            self._update_cost_pricelist(cost_field, values[cost_field])
        return res
    
    def action_view_costs_pricelist_items(self):
        self.ensure_one()
        action = self.env.ref(
            "mrp_unbuild_cust_alu_analytics_valuation.action_product_pricelist_item"
        ).read()[0]
        action["domain"] = [('pricelist_id.unbuild_process_type_id', '=', self.id)]
        return action
    
    def _get_costs_fields_dict(self):
        return {field[0]: field[1] for field in COST_UNIT_SELECTION_FIELDS}

    def _get_costs_fields(self):
        return list(self._get_costs_fields_dict().keys())

    def _create_costs_pricelists(self):
        priceslist_vals_list = []
        cost_field_dict = self._get_costs_fields_dict()
        cost_field_keys = self._get_costs_fields()
        today = fields.Date.today()
        yesterday = today - timedelta(days=1)
        for type in self:
            for field in cost_field_keys:
                item_list = [(0, 0 , {
                    "applied_on": "3_global",
                    "date_end": yesterday,
                    "compute_price": "fixed",
                    "fixed_price": type[field],                    
                })]
                item_list.append((0, 0, {
                    "applied_on": "3_global",
                    "date_start": today,
                    "compute_price": "fixed",
                    "fixed_price": type[field],                    
                }))
                priceslist_vals_list.append({
                    "unbuild_process_type_id": type.id,
                    "unbuild_process_type_cost": field,
                    "company_id": type.company_id.id,
                    "name": f"{type.name} - {cost_field_dict[field]}",
                    "active": False,
                    "item_ids": item_list,
                })
        if priceslist_vals_list:
            self.env["product.pricelist"].sudo().create(priceslist_vals_list)

    def _update_cost_pricelist(self, cost_field, cost_value):
        for type in self:
            type.with_context(active_test=False).sudo().cost_pricelist_ids.filtered(
                lambda x: x.unbuild_process_type_cost == cost_field
            )._update_cost_value(cost_value)

    def _get_costs(self, production_id):
        self.ensure_one()
        et = production_id.shift_effective_time
        qty = production_id.product_uom_id._compute_quantity(
            production_id.product_qty, self.cost_unit_uom_id
        )
        costs = {
            "cost_extra_pt_manpower": et * self._get_cost(production_id, "cost_hr_manpower"),
            "cost_extra_pt_energy": et * self._get_cost(production_id, "cost_hr_energy"),
            "cost_extra_pt_amortization": et * self._get_cost(production_id, "cost_hr_amortization"),
            "cost_extra_pt_repair_maintenance_mgmt": et * self._get_cost(production_id, "cost_hr_repair_maintenance_mgmt"),
            "cost_extra_pt_consumable": qty * self._get_cost(production_id, "cost_unit_consumable"),
            "cost_extra_pt_maquila": qty * self._get_cost(production_id, "cost_unit_maquila"),
        }
        costs.update({
            "cost_extra_process_type": sum(costs[k] for k in costs.keys())
        })

        return costs
    
    def _get_cost(self, production_id, cost_field):
        self.ensure_one()
        cost_pricelist_id = self.with_context(
            active_test=False
        ).cost_pricelist_ids.filtered(
            lambda x: x.unbuild_process_type_cost == cost_field
        )
        if cost_pricelist_id:
            price, rule_id = cost_pricelist_id.get_product_price_rule(
                production_id.product_id, 1.0, False, date=production_id.unbuild_date
            )
            return price
        return 0.0
