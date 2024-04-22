# © 2021 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (https://www.gnu.org/licenses/lgpl-3.0.html)

from odoo import api, fields, models


class QcInspection(models.Model):
    _inherit = "qc.inspection"

    unbuild_id = fields.Many2one(
        comodel_name="mrp.unbuild",
        readonly=True,
    )
    rel_unbuild_product_id = fields.Many2one(
        comodel_name="product.product",
        compute="_compute_rel_unbuild_product_id",
        store=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
        string="Related unbuild product",
    )

    @api.depends("unbuild_id", "object_id")
    def _compute_rel_unbuild_product_id(self):
        for inspection in self.filtered(lambda x: (
            x.unbuild_id
            and x.object_id
            and x.object_id._name == "stock.move"
        )):
            inspection.rel_unbuild_product_id = inspection.object_id.product_id

    @api.depends("unbuild_id")
    def _compute_product_id(self):
        super()._compute_product_id()
        for inspection in self.filtered(
            lambda x: x.unbuild_id and not x.object_id
        ):
            inspection.product_id = inspection.unbuild_id.product_id
