# © 2024 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (https://www.gnu.org/licenses/lgpl-3.0.html)

from odoo import api, fields, models

class MrpBom(models.Model):
    _inherit = "mrp.bom"

    process_type_id = fields.Many2one('mrp.unbuild.process.type', string='Process type')