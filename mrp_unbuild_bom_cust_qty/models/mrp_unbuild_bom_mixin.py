# © 2021 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (http://www.gnu.org/licenses/lgpl-3.0.html)

from odoo import fields, models


class MrpUnbuildBoMMixin(models.AbstractModel):
    _name = "mrp.unbuild.bom.mixin"

    name = fields.Char(
        string="Description",
        readonly=False,
    )
    unbuild_id = fields.Many2one(
        comodel_name="mrp.unbuild",
        readonly=True,
        index=True,
        ondelete="cascade",
    )
    bom_id = fields.Many2one(
        comodel_name="mrp.bom",
        related="unbuild_id.bom_id",
        store=True,
    )
    bom_line_id = fields.Many2one(
        comodel_name="mrp.bom.line",
        required=True,
        check_company=True,
        string="Related BoM Line",
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        related="unbuild_id.company_id",
        store=True,
    )

    check_bom_line = fields.Boolean(
        compute="_compute_check_bom_line",
        help="Indicates if this BoM line belongs to the original BoM list",
    )
    bom_line_ids = fields.Many2many(
        related="unbuild_id.bom_line_ids"
    )

    def _compute_check_bom_line(self):
        for record in self:
            if record.bom_line_id.bom_id == record.bom_id:
                record.check_bom_line = True
            else:
                record.check_bom_line = False
