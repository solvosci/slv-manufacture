# © 2024 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3.0 (https://www.gnu.org/licenses/agpl-3.0.html)

from odoo import fields, models

class MrpUnbuildBomQuants(models.Model):
    _inherit = "mrp.unbuild.bom.quants"

    def save_and_new(self):
        self.ensure_one()
        self.unbuild_id.product_qty = sum(self.unbuild_id.bom_quants_total_ids.mapped('total_qty'))
        return super(MrpUnbuildBomQuants, self).save_and_new()

    def save_and_close(self):
        self.ensure_one()
        self.unbuild_id.product_qty = sum(self.unbuild_id.bom_quants_total_ids.mapped('total_qty'))
        return super(MrpUnbuildBomQuants, self).save_and_close()
