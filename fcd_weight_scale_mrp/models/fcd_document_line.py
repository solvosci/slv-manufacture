# © 2022 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html

from odoo import models, fields, api


class FCDDocumentLine(models.Model):
    _inherit = "fcd.document.line"

    move_ids = fields.One2many('stock.move', 'fcd_document_line_id')
    log_ids = fields.One2many('fcd.weight.scale.log', 'fcd_document_line_id')
    production_id = fields.Many2one('mrp.production')
    quantity_real_kg = fields.Float(related="purchase_order_line_id.qty_received", store=True)
    price_real_kg = fields.Float(compute ='_compute_price_real_kg', store=True)
    revised_subtotal = fields.Monetary(related='purchase_order_line_id.price_subtotal', store=True, readonly=False, string="Revised Subtotal")

    @api.depends('revised_subtotal','quantity_real_kg')
    def _compute_price_real_kg (self):
        for record in self:
            if record.quantity_real_kg > 0:
                record.price_real_kg = (record.revised_subtotal) / record.quantity_real_kg
            else:
                record.price_real_kg = 0
