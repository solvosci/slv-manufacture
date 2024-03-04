# © 2024 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (https://www.gnu.org/licenses/lgpl-3.0.html)

from odoo import _, models, fields, api
from odoo.exceptions import ValidationError


class QcInspection(models.Model):
    _inherit = "qc.inspection"

    mrp_unbuild_id = fields.Many2one(comodel_name="mrp.unbuild", compute="_compute_mrp_unbuild_id", store=True)

    # @api.model
    # def create(self, vals):
    #     record = super(QcInspection, self).create(vals)
    #     if self.env.context.get('unbuild'):
    #         record.inspection_lines =  record._prepare_inspection_lines(record.test)
    #     return record

    def object_selection_values(self):
        result = super().object_selection_values()
        result.extend(
            [
                ("mrp.unbuild", "Unbuild Order"),
            ]
        )
        return result

    @api.depends("object_id")
    def _compute_mrp_unbuild_id(self):
        for inspection in self:
            if inspection.object_id and inspection.object_id._name == "mrp.unbuild":
                inspection.mrp_unbuild_id = inspection.object_id
            else:
                inspection.mrp_unbuild_id = False