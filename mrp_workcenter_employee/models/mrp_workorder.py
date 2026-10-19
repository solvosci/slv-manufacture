# © 2026 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class MrpWorkorder(models.Model):
    _inherit = "mrp.workorder"

    employee_id = fields.Many2one(
        "hr.employee",
        string="Employee",
        help="Employee who is responsible for this work order.",
        compute="_compute_workcenter_employee",
        store=True,
        readonly=False,
    )

    @api.depends("workcenter_id")
    def _compute_workcenter_employee(self):
        for workorder in self:
            is_valid = workorder.employee_id in workorder.workcenter_id.employee_ids
            workorder.employee_id = workorder.employee_id if is_valid else False

    @api.constrains("employee_id", "workcenter_id", "workcenter_id.employee_ids")
    def _check_employee_in_workcenter(self):
        for workorder in self.filtered(lambda w: w.employee_id not in workorder.workcenter_id.employee_ids):
            raise ValidationError(
                _("%(employee)s does not work in the work center %(workcenter)s.")
                % {
                    "employee": workorder.employee_id.display_name,
                    "workcenter": workorder.workcenter_id.display_name,
                }
            )
