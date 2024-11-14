# © 2024 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See https://www.gnu.org/licenses/lgpl-3.0.html

from odoo import models


class ManufactureOrder(models.Model):
    _inherit = "mrp.production"

    def _prepare_mark_account_move_ids(self):
        res = super(ManufactureOrder, self)._prepare_mark_account_move_ids()

        pol_obj = self.env['purchase.order.line'].sudo()
        for move in self.move_raw_ids.filtered(lambda x: x.state == "done"):        
            project_id = move.raw_material_production_id.project_id
            # TODO: Check slow query
            mr_qty = sum(self.sudo().search([('project_id', '=', project_id.id), ('state', '=', 'done')]).move_raw_ids.filtered(lambda x: x.product_id == move.product_id.id).mapped('quantity_done'))
            mt_total = mr_qty + move.product_uom_qty
            pol_qty = sum(pol_obj.search([('account_analytic_id', '=', project_id.analytic_account_id.id), ('state', 'in', ['purchase', 'done']), ('product_id', '=', move.product_id.id)]).mapped('product_uom_qty'))

            if mt_total <= pol_qty:
                res |= move.sudo().mapped('account_move_ids.line_ids')

        return res
