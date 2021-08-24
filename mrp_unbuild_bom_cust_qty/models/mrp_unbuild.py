# © 2021 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (https://www.gnu.org/licenses/lgpl-3.0.html)

from odoo import _, api, models, fields
from odoo.exceptions import ValidationError


class MrpUnbuild(models.Model):
    _inherit = "mrp.unbuild"

    bom_custom_quants = fields.Boolean(
        string="Fill Custom Quants",
        default=True,
        compute="_compute_bom_quants_standard",
        readonly=False,
        store=True,
        help="When selected, you'll be able to add custom quants for unbuild,"
        " and standard ones are not used"
    )
    bom_quants_ids = fields.One2many(
        comodel_name="mrp.unbuild.bom.quants",
        inverse_name="unbuild_id",
        string="BoM Quants",
        readonly=False,
        states={'done': [('readonly', True)]},
        copy=False,
    )
    bom_quants_total_ids = fields.One2many(
        comodel_name="mrp.unbuild.bom.totals",
        inverse_name="unbuild_id",
        string="BoM Quant Totals",
        copy=False,
    )

    bom_quants_has_totals = fields.Boolean(
        compute="_compute_bom_quants_has_totals",
    )

    def _compute_bom_quants_has_totals(self):
        for record in self:
            if record.bom_quants_total_ids.filtered(lambda x: x.total_qty > 0):
                record.bom_quants_has_totals = True
            else:
                record.bom_quants_has_totals = False

    @api.model
    def create(self, values):
        rec = super().create(values)
        if not rec.mo_id:
            for bom_line in rec.bom_id.bom_line_ids:
                # TODO Review values are not saved
                rec.bom_quants_total_ids = [(
                    0,
                    0,
                    {'bom_line_id': bom_line.id}
                )]
        return rec

    @api.depends("mo_id")
    def _compute_bom_quants_standard(self):
        # TODO set again value when mo_id unset?
        for record in self.filtered("mo_id"):
            record.bom_custom_quants = False

    def action_validate(self):
        self.ensure_one()
        if self.bom_custom_quants:
            bom_total_errors = []
            for record in self.bom_quants_total_ids:
                if record.total_qty == 0.0 and record.expected_qty > 0.0:
                    bom_total_errors.append(record.bom_line_id.product_id.display_name)
            if bom_total_errors:
                error_totals = ''
                for error in bom_total_errors:
                    error_totals += (("- %s\n") % (error))
                raise ValidationError(_(
                    "Insufficient quantities for\n\n%s\n"
                    "You should register at least one quantity,"
                    " or unset expected quantity for them"
                ) % error_totals)
        return super().action_validate()

    def _generate_move_from_bom_line(self, product, product_uom, quantity, bom_line_id=False, byproduct_id=False):
        # Default BoM line quantity is overwritten by custom ones
        if self.bom_custom_quants and bom_line_id:
            bom_line_obj = self.bom_quants_total_ids.filtered(lambda x: x.bom_line_id.id == bom_line_id)
            quantity = bom_line_obj.total_qty

        return super()._generate_move_from_bom_line(product, product_uom, quantity, bom_line_id=bom_line_id, byproduct_id=byproduct_id)
