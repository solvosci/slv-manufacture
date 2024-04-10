# © 2024 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (https://www.gnu.org/licenses/lgpl-3.0.html)

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    group_unbuild_force_exact_qty = fields.Boolean(
        implied_group="mrp_unbuild_bom_cust_qty.group_unbuild_force_exact_qty",
        string="Unbuilds: force quantity unbuilt from BoM quants",
    )
