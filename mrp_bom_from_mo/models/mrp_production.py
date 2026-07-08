# © 2026 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See https://www.gnu.org/licenses/lgpl-3.0.html

from odoo import _, models


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    def action_open_bom_from_mo_wizard(self):
        self.ensure_one()
        return {
            'name': _('Create Bill of Materials'),
            'type': 'ir.actions.act_window',
            'res_model': 'mrp.bom.from.mo.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_production_id': self.id,
            },
        }
