# © 2026 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

import logging
_logger = logging.getLogger(__name__)

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

    is_mrp_manager = fields.Boolean(
        compute="_compute_is_mrp_manager",
    )

    def _compute_is_mrp_manager(self):
        self.is_mrp_manager = self.env.user.has_group("mrp.group_mrp_manager")

    # In both methods, employee must remain
    # even if deleted from the workcenter for consistency
    # with the workorder history.
    # This is why workcenter_id.employee_ids is not part of depends/constrains
    # field list
    @api.depends("workcenter_id", "state")
    def _compute_workcenter_employee(self):
        for workorder in self.filtered(lambda x: x.state not in ["done", "cancel"]):
            is_valid = workorder.employee_id in workorder.workcenter_id.employee_ids
            workorder.employee_id = workorder.employee_id if is_valid else False

    @api.constrains("employee_id", "workcenter_id")
    def _check_employee_in_workcenter(self):
        for workorder in self.filtered(
            lambda w: w.employee_id and w.employee_id not in w.workcenter_id.employee_ids
        ):
            raise ValidationError(
                _("%(employee)s does not work in the work center %(workcenter)s.")
                % {
                    "employee": workorder.employee_id.display_name,
                    "workcenter": workorder.workcenter_id.display_name,
                }
            )
