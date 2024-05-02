# © 2024 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (https://www.gnu.org/licenses/lgpl-3.0.html)

from odoo import models, fields

class MrpBomLine(models.Model):
    _inherit = "mrp.bom.line"

    disabled_mrp_unbuild_valuation = fields.Boolean(
        string='Disabled for manufacturing/unbuild',
        default=False
    )
