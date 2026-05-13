# © 2026 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import fields, models


class QcTriggerPickingTypeLine(models.Model):
    _name = "qc.trigger.picking_type_line"
    _inherit = "qc.trigger.line"
    _description = "Quality Control Trigger Picking Type Line"

    picking_type_id = fields.Many2one(
        comodel_name="stock.picking.type",
        string="Picking Type",
        ondelete="cascade"
    )

    def get_trigger_line_for_picking_type(self, trigger, picking_type, partner=False):
        trigger_lines = self.search([
            ('trigger', '=', trigger.id),
            ('picking_type_id', '=', picking_type.id),
        ])
        res = set()
        for line in trigger_lines:
            if not line.partners or (partner and partner.commercial_partner_id in line.partners):
                res.add(line)
        return res
