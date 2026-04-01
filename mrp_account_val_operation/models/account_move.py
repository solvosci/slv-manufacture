# © 2026 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See https://www.gnu.org/licenses/lgpl-3.0.html
from odoo import models, fields
class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    val_operation = fields.Selection(
        selection_add=[
        ('mrp_cons', 'Manufacture Consumption'),
        ('mrp_prod', 'Manufacture Production'),
        ('ub_cons', 'Disassembly - Re-entry of consumed items'),
        ('ub_prod', 'Disassembly - Previously produced items')],
    )

    def _compute_val_operation(self):
        super()._compute_val_operation()
        lines_with_move = self.filtered(
            lambda l: l.move_id.stock_move_id and
            (l.move_id.stock_move_id.raw_material_production_id or
            l.move_id.stock_move_id.production_id or
            l.move_id.stock_move_id.unbuild_id)
        )
        for line in lines_with_move:
            move = line.move_id.stock_move_id
            if line.val_operation == 'in_return' and move.unbuild_id:
                line.val_operation = 'ub_cons'
            elif line.val_operation == 'out_return' and move.unbuild_id:
                line.val_operation = 'ub_prod'
            elif move.raw_material_production_id:
                line.val_operation = 'mrp_cons'
            elif move.production_id:
                line.val_operation = 'mrp_prod'

    def _get_val_operation_origin_target(self):
        res_id, res_model = super()._get_val_operation_origin_target()
        if res_id and res_model:
            return res_id, res_model
        move = self.move_id.stock_move_id
        if move.unbuild_id:
            return move.unbuild_id.id, 'mrp.unbuild'
        elif move.raw_material_production_id:
            return move.raw_material_production_id.id, 'mrp.production'
        elif move.production_id:
            return move.production_id.id, 'mrp.production'
        return False, False

