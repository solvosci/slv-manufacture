# © 2023 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See https://www.gnu.org/licenses/lgpl-3.0.html

from odoo import models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    def _autoconfirm_production(self):
        mrp = self.with_context(skip_trigger_scheduler=True)
        super(MrpProduction, mrp)._autoconfirm_production()

    def action_confirm(self):
        mrp = self.with_context(skip_trigger_scheduler=True)
        return super(MrpProduction, mrp).action_confirm()
