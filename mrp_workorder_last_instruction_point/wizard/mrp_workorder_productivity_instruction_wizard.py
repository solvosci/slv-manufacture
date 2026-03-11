# © 2026 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html
from odoo import models, fields

class WorkorderProductivityInstructionWizard(models.TransientModel):
    _name = "mrp.workorder.productivity.instruction.wizard"
    _description = "Workorder Productivity Instruction Wizard"

    workorder_id = fields.Many2one("mrp.workorder")
    technical_instruction_point = fields.Text(
        string="Technical Instruction Point",
        required=True,
    )

    def action_confirm(self):
        self.ensure_one()
        wo = self.workorder_id
        timeline = self.workorder_id.time_ids.filtered(
            lambda x: x.user_id == self.env.user and not x.date_end
        )[:1]
        if timeline:
            timeline.technical_instruction_point = self.technical_instruction_point
        wo.with_context(mrp_wo_skip_last_instruction_request=True).button_pending()
        return {"type": "ir.actions.act_window_close"}
