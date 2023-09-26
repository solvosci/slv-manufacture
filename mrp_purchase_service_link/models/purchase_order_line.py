# © 2023 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html

from odoo import models, fields


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    mrp_production_id = fields.Many2one(
        comodel_name='mrp.production',
        readonly=True,
        copy=False,
        string="Service Production",
    )
