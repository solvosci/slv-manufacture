# © 2024 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (https://www.gnu.org/licenses/lgpl-3.0.html)

from odoo import models, fields

class MrpBomLine(models.Model):
    _inherit = "mrp.bom.line"

    disabled_mrp_unbuild_valuation = fields.Boolean(
        string='Disabled for manufacturing/unbuild valuation',
        default=False
    )

    def _get_mrp_unbuild_valuation_to_disable(self):
        self.ensure_one()
        return (
            self.disabled_mrp_unbuild_valuation
            or self.product_id.has_waste_cost_mgmt
            or self.product_id.type not in ["product", "consu"]
        )
