# © 2023 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html

from odoo import models


class MRPProduction(models.Model):
    _inherit = 'mrp.production'

    def _compute_total_cost(self):
        super(MRPProduction, self)._compute_total_cost()
        for record in self:
            for service in record.purchase_line_ids:
                record.total_cost += service.price_subtotal
