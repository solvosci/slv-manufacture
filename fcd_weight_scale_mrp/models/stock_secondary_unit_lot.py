# © 2022 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html

from odoo import models, fields, api


class StockSecondaryUnitLot(models.Model):
    _name = 'stock.secondary.unit.lot'
    _description = 'Stock Secondary Unit Lot'

    name = fields.Char(compute="_compute_name", store=True)
    lot_id = fields.Many2one('stock.production.lot')
    move_line_ids = fields.Many2many('stock.move.line')
    secondary_uom_id = fields.Many2one('product.secondary.unit', string="Type Box")
    secondary_uom_qty = fields.Integer(compute="_compute_secondary_uom_qty", string="Qty")

    @api.depends('secondary_uom_id.name', 'move_line_ids.secondary_uom_qty')
    def _compute_name(self):
        for record in self:
            record.name = "%s (%s)" % (record.secondary_uom_id.name, record.secondary_uom_qty)

    # @api.depends('move_line_ids', 'move_line_ids.secondary_uom_qty')
    def _compute_secondary_uom_qty(self):
        for record in self:
            incoming = sum(record.move_line_ids.filtered(lambda x: x.picking_code == 'incoming').mapped('secondary_uom_qty'))
            outgoing = -sum(record.move_line_ids.filtered(lambda x: x.picking_code == 'outgoing').mapped('secondary_uom_qty'))
            internal = sum(record.move_line_ids.filtered(lambda x: x.picking_code == 'internal').mapped('secondary_uom_qty'))
            mrp_operation = sum(record.move_line_ids.filtered(lambda x: x.picking_code == 'mrp_operation').mapped('secondary_uom_qty'))

            mrp_incoming = sum(record.move_line_ids.filtered(lambda x: x.picking_code == False and x.location_dest_id.usage == 'internal').mapped('secondary_uom_qty'))
            mrp_outgoing = -sum(record.move_line_ids.filtered(lambda x: x.picking_code == False and x.location_dest_id.usage == 'production').mapped('secondary_uom_qty'))

            record.secondary_uom_qty = int(incoming + outgoing + internal + mrp_operation + mrp_incoming + mrp_outgoing)
