# © 2025 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html
from odoo import api, models


class MrpProduction(models.Model):
    _name = "mrp.production"
    _inherit = ["mrp.production", "sn.locked.mixin"]

    @api.depends("state")
    def _compute_sn_locked_invisible(self):
        super()._compute_sn_locked_invisible()
        locked_inv_mrp_ids = self.filtered(
            lambda x: x.state not in ["confirmed", "progress"]
        )
        locked_inv_mrp_ids.update({"sn_locked_invisible": True})
        (self - locked_inv_mrp_ids).update({"sn_locked_invisible": False})
