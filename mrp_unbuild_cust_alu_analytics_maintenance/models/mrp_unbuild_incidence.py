# © 2024 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (https://www.gnu.org/licenses/lgpl-3.0.html)

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class MrpUnbuildIncidence(models.Model):
    _inherit = "mrp.unbuild.incidence"

    maintenance_equipment_id = fields.Many2one('maintenance.equipment', string='Maintenance Equipment', domain=[('works_with_unbuild', '=', True)])