# © 2022 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See https://www.gnu.org/licenses/lgpl-3.0.html

from odoo import api, models
from odoo.tools import float_is_zero


class MrpBom(models.Model):
    _inherit = "mrp.bom"

    @api.model
    def create(self, values):
        res = super(MrpBom, self).create(values)
        res.update_product_standard_price()
        return res

    @api.multi
    def write(self, values):
        """
        Some changes in BoM or BoM lines should alter product standard price
        """
        res = super(MrpBom, self).write(values)
        upd_fields = ["bom_line_ids", "product_tmpl_id", "product_qty", "active"]
        val_keys = values.keys()
        if any(f in val_keys for f in upd_fields):
            # One special case should be active change, that should affect to
            #  active BoM, so we have to recalculate current BoM and self
            #  cannot be directly used
            self.product_tmpl_id.bom_ids.update_product_standard_price()
        return res

    @api.multi
    def unlink(self):
        product_tmpls = self.mapped("product_tmpl_id")
        res = super(MrpBom, self).unlink()
        product_tmpls.bom_ids.update_product_standard_price()
        return res

    @api.multi
    def update_product_standard_price(self):
        """
        Updates standard_price for the products involved in this BoMs
        based on an AVCO method from BoM lines
        """
        # Only proper cost method product with a single BoM and single variant
        #  will be updated
        for bom in self.filtered(
            lambda x: x.product_tmpl_id.cost_method == "standard"
            and len(x.product_tmpl_id.bom_ids) == 1
            and len(x.product_tmpl_id.product_variant_ids) == 1
        ):
            if float_is_zero(
                bom.product_qty,
                precision_rounding=bom.product_uom_id.rounding
            ):
                bom.product_tmpl_id.product_variant_ids.standard_price = 0.0
            else:
                bom.product_tmpl_id.product_variant_ids.standard_price = sum(
                    bl.product_qty * bl.product_id.standard_price
                    for bl in bom.bom_line_ids
                ) / bom.product_qty
