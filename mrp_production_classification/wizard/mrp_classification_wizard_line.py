# Copyright 2026 Solvos Consultoría Informática, S.L. (<https://www.solvos.es>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import fields, models
from odoo.exceptions import UserError


class MrpClassificationWizardLine(models.TransientModel):
    _name = "mrp.classification.wizard.line"
    _description = "Classification Distribution Line"

    wizard_id = fields.Many2one(
        "mrp.classification.wizard", required=True, ondelete="cascade"
    )
    move_id = fields.Many2one(
        "stock.move",
        required=True,
        readonly=True,
        help="Original move of the finished product/byproduct in the MO.",
    )
    product_id = fields.Many2one("product.product", required=True, readonly=True)
    product_tracking = fields.Selection(related="product_id.tracking")

    product_uom_id = fields.Many2one("uom.uom", required=True, readonly=True)

    qty = fields.Float(
        string="Classified Quantity", digits="Product Unit", required=True
    )

    lot_id = fields.Many2one(
        "stock.lot",
        string="Existing Lot",
        domain="[('product_id', '=', product_id)]",
    )
    lot_name = fields.Char(
        string="Lot Name to Create",
    )

    def _get_or_create_lot(self):
        self.ensure_one()
        if self.lot_id:
            return self.lot_id

        if not self.lot_name:
            raise UserError(
                self.env._("You must specify an existing lot or a lot name.")
            )

        company = self.wizard_id.production_id.company_id
        lot = self.env["stock.lot"].search(
            [
                ("product_id", "=", self.product_id.id),
                ("name", "=", self.lot_name),
                ("company_id", "=", company.id),
            ],
            limit=1,
        )
        if not lot:
            lot = self.env["stock.lot"].create(
                {
                    "product_id": self.product_id.id,
                    "name": self.lot_name,
                    "company_id": company.id,
                }
            )
        self.lot_id = lot
        return lot
