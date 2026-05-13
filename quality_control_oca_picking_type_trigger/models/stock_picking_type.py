# © 2026 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import fields, models


class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    qc_triggers = fields.One2many(
        comodel_name="qc.trigger.picking_type_line",
        inverse_name="picking_type_id",
        string="Quality control triggers",
    )
