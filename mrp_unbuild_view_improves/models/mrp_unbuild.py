# © 2024 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (https://www.gnu.org/licenses/lgpl-3.0.html)

from odoo import models, fields


class MrpUnbuild(models.Model):
    _inherit = "mrp.unbuild"

    bom_code = fields.Char(
        string="Bom Code",
        related="bom_id.code",
    )
