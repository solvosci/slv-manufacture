# © 2024 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3.0 (https://www.gnu.org/licenses/agpl-3.0.html)

from odoo import fields, models


class MrpUnbuild(models.Model):
    _inherit = "mrp.unbuild"

    created_inspections = fields.Integer(
        compute="_compute_count_inspections", string="Created inspections"
    )
    done_inspections = fields.Integer(
        compute="_compute_count_inspections", string="Done inspections"
    )
    passed_inspections = fields.Integer(
        compute="_compute_count_inspections", string="Inspections OK"
    )
    failed_inspections = fields.Integer(
        compute="_compute_count_inspections", string="Inspections failed"
    )

    def _compute_count_inspections(self):
        data = (
            self.env["qc.inspection"]
            .sudo()
            .read_group(
                [("unbuild_id", "in", self.ids)],
                ["unbuild_id", "state"],
                ["unbuild_id", "state"],
                lazy=False,
            )
        )
        unbuild_data = {}
        for d in data:
            unbuild_data.setdefault(d["unbuild_id"][0], {}).setdefault(d["state"], 0)
            unbuild_data[d["unbuild_id"][0]][d["state"]] += d["__count"]
        for unbuild in self:
            count_data = unbuild_data.get(unbuild.id, {})
            unbuild.created_inspections = sum(count_data.values())
            unbuild.passed_inspections = count_data.get("success", 0)
            unbuild.failed_inspections = count_data.get("failed", 0)
            unbuild.done_inspections = (
                unbuild.passed_inspections + unbuild.failed_inspections
            )