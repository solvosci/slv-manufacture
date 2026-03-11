# © 2026 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html
from odoo import models, fields, api, _


class MrpWorkorder(models.Model):
    _inherit = "mrp.workorder"

    last_technical_instruction_point = fields.Text(
        string="Last Technical Point Instruction",
        help="Last technical point instruction given to the operator in this workorder.",
        compute="_compute_last_technical_instruction_data",
    )

    last_technical_instruction_point_user_id = fields.Many2one(
        "res.users",
        string="Last Technical Point Instruction User",
        help="User who created the last technical point instruction.",
        compute="_compute_last_technical_instruction_data",
    )

    @api.depends("time_ids.technical_instruction_point", "time_ids.user_id", "state")
    def _compute_last_technical_instruction_data(self):
        wo_progress = self.filtered(
            lambda x: x.time_ids.filtered("date_end") and x.state == "progress"
        )
        for workorder in wo_progress:
            last_time = workorder.time_ids.filtered(
                lambda t: t.date_end
            ).sorted(lambda t: t.date_end)[-1]
            workorder.update({
                "last_technical_instruction_point": last_time.technical_instruction_point,
                "last_technical_instruction_point_user_id": last_time.user_id.id,
            })
        (self - wo_progress).update({
            "last_technical_instruction_point": False,
            "last_technical_instruction_point_user_id": False,
        })

    def button_pending(self):
        self.ensure_one()
        if self.env.context.get("mrp_wo_skip_last_instruction_request", False):
            return super().button_pending()
        else:
            return {
                "type": "ir.actions.act_window",
                "name": _("Technical Instruction Point"),
                "res_model": "mrp.workorder.productivity.instruction.wizard",
                "view_mode": "form",
                "target": "new",
                "context": {
                    "default_workorder_id": self.id,
                },
            }
