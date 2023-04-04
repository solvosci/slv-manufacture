# © 2023 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html

from odoo import models, fields, _


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    fcd_log_ids = fields.One2many('fcd.weight.scale.log', 'purchase_order_line_id')
    fcd_log_count = fields.Char('Weighings', compute="_compute_fcd_log_count")

    def _compute_fcd_log_count(self):
        for record in self:
            record.fcd_log_count = _('%s Weighings') % (len(record.fcd_log_ids))

    def emergent_remove_log_open_wizard(self):
        self.ensure_one()
        Wizard = self.env['fcd.weight.scale.mrp.wizard']

        new = Wizard.create({
            'purchase_line_id': self.id,
        })

        return {
            'name': _('WARNING!!'),
            'res_model': 'fcd.weight.scale.mrp.wizard',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': new.id,
            'target': 'new',
            'type': 'ir.actions.act_window'
        }
