# © 2026 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import models
from odoo.addons.quality_control_oca.models.qc_trigger_line import _filter_trigger_lines

class StockPicking(models.Model):
    _inherit = "stock.picking"

    def _action_done(self):
        res = super()._action_done()
        inspection_model = self.env["qc.inspection"].sudo()
        qc_triggers = self.env["qc.trigger"].sudo().search([
            ("picking_type_id", "=", self.picking_type_id.id)
        ])
        for qc_trigger in qc_triggers:
            partner = self.partner_id if qc_trigger.partner_selectable else False
            trigger_lines = self.env["qc.trigger.picking_type_line"].sudo().get_trigger_line_for_picking_type(
                qc_trigger,
                self.picking_type_id,
                partner=partner
            )
            for trigger_line in _filter_trigger_lines(trigger_lines):
                exists = inspection_model.search([
                    ('object_id', '=', 'stock.picking,%d' % self.id),
                    ('test', '=', trigger_line.test.id)
                ], limit=1)
                if not exists:
                    inspection_model._make_inspection(self, trigger_line)
        return res
