# © 2024 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (https://www.gnu.org/licenses/lgpl-3.0.html)

from odoo import models, fields

class MrpBomLine(models.Model):
    _inherit = "mrp.bom.line"

    no_manufacture_unbuild_valuation = fields.Boolean(
        string='No valuation for manufacturing/unbuild',
        default=False
    )
