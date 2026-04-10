# © 2026 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See https://www.gnu.org/licenses/lgpl-3.0.html
from odoo import models, fields


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    val_operation = fields.Selection(
        selection_add=[
            ('repair_add', 'Repair - Component Added'),
            ('repair_remove', 'Repair - Component Removed'),
        ],
    )

    def _compute_val_operation(self):
        super()._compute_val_operation()
        lines_with_repair = self.filtered(lambda l: l.move_id.stock_move_id.repair_id)
        lines_repair_remove = lines_with_repair.filtered(lambda l: l.move_id.stock_move_id.location_id.usage == 'production')
        lines_repair_remove.val_operation = 'repair_remove'
        (lines_with_repair - lines_repair_remove).val_operation = 'repair_add'

        # We do NOT use repair.line.type because there is no direct
        # relationship between account.move.line and repair.line without relying on product_id matching.
        # That approach becomes ambiguous when multiple repair lines exist for the same product.
        # Therefore, classification is derived from the stock flow direction.


    def _get_val_operation_origin_target(self):
        res_id, res_model = super()._get_val_operation_origin_target()
        if res_id and res_model:
            return res_id, res_model
        move = self.move_id.stock_move_id
        if move and move.repair_id:
            return move.repair_id.id, 'repair.order'
        return False, False
