# © 2025 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See https://www.gnu.org/licenses/lgpl-3.0.html

from odoo import models


class MrpUnbuild(models.Model):
    _inherit = "mrp.unbuild"

    def action_unbuild(self):
        res = super().action_unbuild()
        if self.mo_id:
            self._update_analytic_mrp_unbuilt()
        return res

    def _update_analytic_mrp_unbuilt(self):
        self.ensure_one()
        done_moves = (self.mo_id.move_raw_ids + self.mo_id.move_finished_ids).filtered(
            lambda x: x.state == "done"
        )
        aml_ids = done_moves.sudo().mapped('account_move_ids.line_ids')
        aml_ids.write({
            "analytic_mrp_unbuilt": True,
        })
