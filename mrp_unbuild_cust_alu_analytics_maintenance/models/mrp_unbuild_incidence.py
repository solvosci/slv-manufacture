# © 2024 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3.0 (https://www.gnu.org/licenses/agpl-3.0.html)

from odoo import fields, models

class MrpUnbuildIncidence(models.Model):
    _inherit = "mrp.unbuild.incidence"

    maintenance_equipment_id = fields.Many2one('maintenance.equipment', string='Maintenance Equipment', domain=[('works_with_unbuild', '=', True)])
