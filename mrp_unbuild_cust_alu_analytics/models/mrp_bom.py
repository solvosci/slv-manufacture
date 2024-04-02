# © 2024 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3.0 (https://www.gnu.org/licenses/agpl-3.0.html)

from odoo import fields, models

class MrpBom(models.Model):
    _inherit = "mrp.bom"

    process_type_id = fields.Many2one('mrp.unbuild.process.type', string='Process type')