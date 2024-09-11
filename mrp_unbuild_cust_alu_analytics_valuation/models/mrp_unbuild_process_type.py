# © 2024 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3.0 (https://www.gnu.org/licenses/agpl-3.0.html)

from odoo import fields, models

class MrpUnbuildProcessType(models.Model):
    _inherit = "mrp.unbuild.process.type"

    cost_hr_manpower = fields.Monetary(
        "Manpower unit cost",
        currency_field='currency_id',
        default=0.0,        
    )
    cost_hr_energy = fields.Monetary(
        "Energy unit cost",
        currency_field='currency_id',
        default=0.0
    )
    cost_hr_amortization = fields.Monetary(
        "Amortization unit cost",
        currency_field='currency_id',
        default=0.0
    )
    cost_hr_repair_maintenance_mgmt = fields.Monetary(
        'Repair/Maintenance management unit cost',
        currency_field='currency_id',
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
    )
    cost_unit_maquila = fields.Monetary(
        string="Maquilas unit cost (by unit)",
    )

    def _get_costs(self, production_id):
        self.ensure_one()
        et = production_id.shift_effective_time
        qty = production_id.product_uom_id._compute_quantity(
            production_id.product_qty, self.cost_unit_uom_id
        )
        costs = {
            "cost_extra_pt_manpower": et * self.cost_hr_manpower,
            "cost_extra_pt_energy": et * self.cost_hr_energy,
            "cost_extra_pt_amortization": et * self.cost_hr_amortization,
            "cost_extra_pt_repair_maintenance_mgmt": et * self.cost_hr_repair_maintenance_mgmt,
            "cost_extra_pt_consumable": qty * self.cost_unit_consumable,
            "cost_extra_pt_maquila": qty * self.cost_unit_maquila,
        }
        costs.update({
            "cost_extra_process_type": sum(costs[k] for k in costs.keys())
        })

        return costs
