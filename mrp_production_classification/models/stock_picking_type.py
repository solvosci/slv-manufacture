# Copyright 2026 Solvos Consultoría Informática, S.L. (<https://www.solvos.es>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    is_classification = fields.Boolean(
        string="Is Classification Operation",
        help="Enables the distribution wizard on "
        "manufacturing orders associated with this operation type.",
    )
