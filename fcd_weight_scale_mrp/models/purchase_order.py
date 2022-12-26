# © 2022 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html

from odoo import models


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def action_purchase_order_confirm_multi(self):
        super(PurchaseOrder, self).action_purchase_order_confirm_multi()
        for picking_id in self.browse(self.env.context['active_ids']).filtered(lambda x: x.state == 'purchase').picking_ids.filtered(lambda x: x.state in ('draft', 'waiting', 'confirmed', 'assigned')):
            for move_id in picking_id.move_ids_without_package:
                move_id.action_complete_stock_move_line()
            picking_id.button_validate()
