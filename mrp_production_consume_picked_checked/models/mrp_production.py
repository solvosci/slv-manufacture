# © 2026 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html

from odoo import models

class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    def _post_inventory(self, cancel_backorder=False):
        moves_to_consume = self.move_raw_ids.filtered(
            lambda m: m.state not in ('done', 'cancel')
            and m.product_uom_qty == 0.0
            and m.quantity > 0.0
            and not m.picked
        )
        if moves_to_consume:
            moves_to_consume.write({'picked': True})
        return super(MrpProduction, self)._post_inventory(cancel_backorder=cancel_backorder)
