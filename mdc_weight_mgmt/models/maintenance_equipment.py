# # © 2025 Solvos Consultoría Informática (<http://www.solvos.es>)
# # License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html
from odoo import models


class MaintenanceEquipment(models.Model):
    _inherit = 'maintenance.equipment'

    def _get_default_category_id(self):
        context = self.env.context
        if context.get('equipment_category_default_id'):
            return self.env.company.equipment_category_default_id
