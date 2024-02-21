# © 2024 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See https://www.gnu.org/licenses/lgpl-3.0.html

from odoo import _, models
from odoo.exceptions import UserError


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    def _check_immediate(self):
        immediate_productions = super()._check_immediate()
        if self.env.context.get("skip_immediate", False):
            return immediate_productions
        mrp_no_lot = immediate_productions.filtered(
            lambda x: (
                x.product_tracking in ["lot", "serial"]
                and not x.lot_producing_id
            )
        )
        if mrp_no_lot:
            raise UserError(
                _("Lot/serial number must be provided for the following products:\n- %s")
                % "\n- ".join(mrp_no_lot.mapped("product_id.display_name"))
            )
        return immediate_productions
