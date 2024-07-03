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

    def _get_costs(self, total_time):
        self.ensure_one()
        return total_time * (
            self.cost_hr_manpower
            + self.cost_hr_energy
            + self.cost_hr_amortization
            + self.cost_hr_repair_maintenance_mgmt
        )
