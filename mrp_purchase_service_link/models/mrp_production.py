# © 2023 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html

from odoo import models, fields


class MRPProduction(models.Model):
    _inherit = "mrp.production"

    purchase_line_ids = fields.Many2many(
        comodel_name='purchase.order.line',
        inverse="_set_purchase_line_ids",
        copy=False,
        string="External Services Purchase Lines",
    )

    def _set_purchase_line_ids(self):
        for record in self:
            if record.purchase_line_ids:
                record.purchase_line_ids.mrp_production_id = record
            all_pol_ids = self.env['purchase.order.line'].search([('mrp_production_id', '=', record.id)])
            remaining_pol = all_pol_ids - record.purchase_line_ids
            remaining_pol.mrp_production_id = False

    def action_cancel(self):
        res = super(MRPProduction, self).action_cancel()
        self.purchase_line_ids = False
        return res
