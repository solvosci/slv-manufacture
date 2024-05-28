# © 2024 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (https://www.gnu.org/licenses/lgpl-3.0.html)

from odoo import models
from odoo.tools.float_utils import float_compare


class ProductHistoryAveragePrice(models.Model):
    _inherit = "product.history.average.price"

    def _update_dependent_svls_pre(self, update_svls):
        """
        For those SVLs to be updated, first recompute cost price,
        that will be later applied to those SVLs
        """
        super()._update_dependent_svls_pre(update_svls)
        unbuild_ids = update_svls.stock_move_id.unbuild_id
        for ub in unbuild_ids:
            ub._update_wo_extra_total()

    def _update_dependent_svls_get_svl_data(self, svl):
        """
        SVL new price unit will be special if it comes from unbuild
        produced move:
        - if it was 0.0 (a produced move that had no value), it remains 0.0
          => equivalent condition == ub_quantity is zero
        - if not, calculated unbuild cost unit price
        """
        unbuild_id = svl.stock_move_id.unbuild_id
        if unbuild_id and float_compare(
            svl.quantity,
            0.0,
            precision_rounding=svl.product_id.uom_id.rounding or 0.001
        ) > 0:
            ub_quantity = svl.stock_move_id._compute_unbuild_svl_quantity(svl.quantity)
            # TODO float_is_zero for ub_quantity
            return (
                ub_quantity and unbuild_id.cost_unit_price
                or 0.0,
                svl.quantity
            )
        else:
            return super()._update_dependent_svls_get_svl_data(svl)
