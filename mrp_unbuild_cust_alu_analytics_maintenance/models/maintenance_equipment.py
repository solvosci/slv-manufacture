# © 2024 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (https://www.gnu.org/licenses/lgpl-3.0.html)

from odoo import _, api, fields, models

class MaintenanceEquipment(models.Model):
    _inherit = "maintenance.equipment"

    works_with_unbuild = fields.Boolean(string='Works with Unbuild', default=False)
