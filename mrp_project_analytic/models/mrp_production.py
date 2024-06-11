# © 2022 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See https://www.gnu.org/licenses/lgpl-3.0.html

from odoo import models


class ManufactureOrder(models.Model):
    _inherit = "mrp.production"

    def write(self, values):
        analytic_account_to_change = (
            "state" in values and values["state"] == "done"
            or
            "project_id" in values
        )
        res = super().write(values)
        if analytic_account_to_change:
            for mrp in self:
                mrp._update_account_analytic()
        return res

    def _update_account_analytic(self):
        self.ensure_one()
        done_moves = (self.move_raw_ids + self.move_finished_ids).filtered(
            lambda x: x.state == "done"
        )
        aml_ids = done_moves.sudo().mapped("account_move_ids.line_ids")
        if aml_ids:
            aml_ids.write({
                "analytic_account_id": (
                    self.sudo().project_id.analytic_account_id.id or False
                ),
            })

    def mark_analytic_mrp_from_child(self):
        child_productions = self._get_children()
        child_products = child_productions.mapped('product_id')
        raw_material_moves = self.move_raw_ids.filtered(
            lambda x: x.state == "done" and x.product_id in child_products
        )
        aml_ids = raw_material_moves.sudo().mapped('account_move_ids.line_ids')
        
        if aml_ids:
            debit_aml_ids = aml_ids.filtered(lambda x: x.debit > 0)
            debit_aml_ids.write({
                "analytic_mrp_from_child": True,
            })
    
    def button_mark_done(self):
        res = super().button_mark_done()
        self.mark_analytic_mrp_from_child()
        return res
