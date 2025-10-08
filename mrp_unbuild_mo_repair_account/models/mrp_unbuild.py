# © 2025 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See https://www.gnu.org/licenses/lgpl-3.0.html

from odoo import models


class MrpUnbuild(models.Model):
    _inherit = "mrp.unbuild"

    def _reconcile_repair_operations_with_moves(self):
        super()._reconcile_repair_operations_with_moves()

        correction_move_ids = self.produce_line_ids.move_line_ids.move_id.sudo().account_move_ids.filtered(lambda x: x.ref == 'Correction of False (modification of past move)')
        for account_move_id in correction_move_ids:
            new_ref = '%s - %s (Correction of past move)' % (self.name, account_move_id.stock_move_id.product_id.name)
            account_move_id.ref = new_ref
            account_move_id.line_ids.name = new_ref
