# Copyright 2026 Solvos Consultoría Informática
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    mrp_step = fields.Selection(
        related='location_dest_id.mrp_step',
        string='Manufacturing Step',
        store=True,
        index=True,
    )