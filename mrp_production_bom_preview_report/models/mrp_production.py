# © 2023 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html

from odoo import models, fields, _


class MRPProduction(models.Model):
    _inherit = 'mrp.production'

    currency_id = fields.Many2one(related="product_id.currency_id", readonly=True)
    total_cost = fields.Monetary(compute='_compute_total_cost', digits='Product Unit of Measure', currency_field='currency_id')

    def _compute_total_cost(self):
        for record in self:
            total_cost = 0
            if record.state == 'done':
                self._context.copy().update({"active_test": False})
                svl_ids = record.env['stock.valuation.layer'].sudo().search([('id', 'in', record.move_raw_ids.stock_valuation_layer_ids.ids)])
                total_cost = sum(svl_ids.mapped('value')) * -1
            else:
                for move in record.move_raw_ids:
                    total_cost += move.product_id.standard_price * move.quantity_done
            record.total_cost = total_cost

    def get_bom_move_report(self):
        if self.state == 'done':
            self._context.copy().update({"active_test": False})
            svl_ids = self.env['stock.valuation.layer'].sudo().search([('id', 'in', self.move_raw_ids.stock_valuation_layer_ids.ids)])
            new_svl_ids = []
            for record in svl_ids:
                new_svl_ids.append(self.env['stock.valuation.layer'].new({
                    'product_id': record.product_id.id,
                    'currency_id': record.currency_id.id,
                    'quantity': record.quantity * -1,
                    'uom_id': record.uom_id.id,
                    'value': record.value * -1
                }))
            return new_svl_ids
        return self.move_raw_ids
