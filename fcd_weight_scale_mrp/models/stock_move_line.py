# © 2022 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html

from odoo import models, fields, api


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    lot_qty = fields.Float(related='lot_id.product_qty')
    # secondary_uom_lot_id = fields.Many2one('stock.secondary.unit.lot', compute="_compute_secondary_uom_lot_id", store=True)

    @api.model
    def _get_secondary_uom_qty_depends(self):
        return super(StockMoveLine, self)._get_secondary_uom_qty_depends()

    @api.depends(lambda x: x._get_secondary_uom_qty_depends())
    def _compute_secondary_uom_qty(self):
        for line in self:
            if not line.move_id.product_id.tracking == 'lot':
                super(StockMoveLine, self)._compute_secondary_uom_qty()

    @api.depends('secondary_uom_id', 'secondary_uom_qty')
    def _compute_product_uom_qty(self):
        for line in self:
            if not line.move_id.product_id.tracking == 'lot':
                super(StockMoveLine, self)._compute_product_uom_qty()

    # @api.depends('secondary_uom_id', 'secondary_uom_qty')
    # def _compute_qty_done(self):
    #     for line in self:
    #         if not line.move_id.product_id.tracking == 'lot':
    #             super(StockMoveLine, self)._compute_qty_done()

    @api.depends("secondary_uom_id", "secondary_uom_qty")
    def _compute_qty_done(self):
        pass

    # @api.depends("state")
    # def _compute_secondary_uom_lot_id(self):
    #     for move_line in self.filtered(lambda x: x.state == 'done'):
    #         if move_line.product_id.stock_secondary_uom_id.id != move_line.secondary_uom_id.id:
    #             secondary_uom_id = move_line.lot_id.secondary_uom_ids.filtered(lambda x: x.secondary_uom_id.id == move_line.secondary_uom_id.id)
    #             if not secondary_uom_id:
    #                 self.env['stock.secondary.unit.lot'].create({
    #                     'lot_id': move_line.lot_id.id,
    #                     'move_line_ids': [(4, move_line.id)],
    #                     'secondary_uom_id': move_line.secondary_uom_id.id,
    #                 })
    #             else:
    #                 secondary_uom_id.write({
    #                     'move_line_ids': [(4, move_line.id)]
    #                 })
