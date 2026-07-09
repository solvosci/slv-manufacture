# © 2022 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html

from odoo import models, fields
import logging

_logger = logging.getLogger(__name__)

class StockProductionLot(models.Model):
    _inherit = "stock.production.lot"

    fcd_document_line_quantity_real_kg = fields.Float(related="fcd_document_line_id.quantity_real_kg")
    fcd_document_line_price_real_kg = fields.Float(related="fcd_document_line_id.price_real_kg")
    fcd_document_line_revised_subtotal = fields.Monetary(related ='fcd_document_line_id.revised_subtotal')

    fcd_origin_lot_id = fields.Many2one('stock.production.lot')
    fcd_relation_lot_ids = fields.One2many('stock.production.lot', 'fcd_origin_lot_id')

    # secondary_uom_ids = fields.One2many('stock.secondary.unit.lot', 'lot_id')

    # @api.depends('product_qty')
    # def _compute_secondary_uom_qty(self):
    #     for record in self:
    #         location_production_id = record.env['stock.location'].search([('usage', '=', 'production')])
    #         in_move_line_ids = record.env['stock.move.line'].search([('lot_id', '=', record.id), ('picking_code', '=', 'incoming')]).mapped("secondary_uom_qty")
    #         out_move_line_ids = record.env['stock.move.line'].search([('lot_id', '=', record.id), ('picking_code', '=', 'outgoing')]).mapped("secondary_uom_qty")

    #         production_move_line_ids = record.env['stock.move.line'].search([('lot_id', '=', record.id), ('picking_code', '=', 'mrp_production')])
    #         in_production_ids = production_move_line_ids.filtered(lambda x: x.location_id.id == location_production_id).mapped("secondary_uom_qty")
    #         out_production_ids = production_move_line_ids.filtered(lambda x: x.location_dest_id.id == location_production_id).mapped("secondary_uom_qty")

    #         # production_total = sum(in_production_ids) - sum(out_production_ids)
    #         record.secondary_uom_qty = sum(in_move_line_ids) + sum(out_production_ids) - sum(out_move_line_ids) - sum(in_production_ids)

    def name_get(self):
        context = self.env.context
        if context.get('fcd_weight_scale_mrp', False):
            result = []
            for lot in self:
                name = "%s (%.2f Kg)" % (
                    lot.name, lot.product_qty
                )
                result.append((lot.id, name))
            return result
        else:
            return super().name_get()

    def check_and_log_stock_balance(self, state, origin=""):
        is_active = self.env['ir.config_parameter'].sudo().get_param('fcd_weight_scale_mrp.enable_lot_logs', default='False') == 'True'
        if not is_active or not self:
            return

        try:
            domain_sml = [('lot_id', '=', self.id), ('state', '=', 'done')]
            move_lines = self.env['stock.move.line'].sudo().search(domain_sml)

            total_sml = 0.0
            for sml in move_lines:
                if sml.location_dest_id.usage == 'internal' and sml.location_id.usage != 'internal':
                    total_sml += sml.qty_done
                elif sml.location_id.usage == 'internal' and sml.location_dest_id.usage != 'internal':
                    total_sml -= sml.qty_done

            quants = self.env['stock.quant'].sudo().search([
                ('lot_id', '=', self.id),
                ('location_id.usage', '=', 'internal')
            ])
            total_quant = sum(quants.mapped('quantity'))

            breakdown = abs(total_sml - total_quant) > 0.001
            log_method = _logger.error if breakdown else _logger.warning

            log_method(
                "[fcd_weight_scale_mrp] Lot: %s | State: %s | Origin: %s | SML Total: %s | Quant Total: %s | Breakdown?: %s",
                self.name, state, origin, total_sml, total_quant, "YES" if breakdown else "NO"
            )

        except Exception as e:
            _logger.error("[fcd_weight_scale_mrp] Error executing logs: %s", e)
