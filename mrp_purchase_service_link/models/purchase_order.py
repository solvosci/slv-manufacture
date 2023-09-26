# © 2023 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html

from odoo import models, fields, _


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    production_ids = fields.Many2many('mrp.production', compute="_compute_production_ids")
    production_count = fields.Integer('Productions', compute="_compute_production_ids")

    def _compute_production_ids(self):
        for record in self:
            record.production_ids = record.order_line.mrp_production_id
            record.production_count = len(record.production_ids)

    def action_mrp_production(self):
        action = {
            'name': _('Productions'),
            'view_mode': 'tree,form',
            'res_model': 'mrp.production',
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', self.production_ids.ids)]
        }
        if self.production_count == 1:
            action["views"] = [
                (self.env.ref("mrp.mrp_production_form_view").id, "form")
            ]
            action["res_id"] = self.production_ids.id
        return action
