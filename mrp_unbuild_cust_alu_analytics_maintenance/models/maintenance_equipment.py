# © 2024 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3.0 (https://www.gnu.org/licenses/agpl-3.0.html)

from odoo import fields, models

class MaintenanceEquipment(models.Model):
    _inherit = "maintenance.equipment"

    works_with_unbuild = fields.Boolean(string='Works with Unbuild', default=False)

    unbuild_count = fields.Integer(
        compute="_compute_count_unbuilds", string="Unbuild Incidences"
    )

    def _compute_count_unbuilds(self):  
        # TODO: this code is inefficient for multiple records, try with read_group
        for record in self:
            incidence_ids = self.env["mrp.unbuild.incidence"].search([("maintenance_equipment_id", "=", record.id)])
            unbuild_ids = incidence_ids.mapped("unbuild_id")
            record.unbuild_count = len(unbuild_ids)
