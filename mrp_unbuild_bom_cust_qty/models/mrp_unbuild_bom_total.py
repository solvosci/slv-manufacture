# © 2021 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (http://www.gnu.org/licenses/lgpl-3.0.html)

from odoo import models, fields, api, _


class MrpUnbuildBoMTotals(models.Model):
    _name = "mrp.unbuild.bom.totals"
    _inherit = "mrp.unbuild.bom.mixin"
    _description = "Quant Totals for BoM based Unbuild"

    expected_qty = fields.Float(
        string="Expected Quantity",
        digits='Product Unit of Measure',
        compute="_compute_expected_qty",
        readonly=False,
        store=True,
    )
    total_qty = fields.Float(
        string="Total Quantity",
        digits='Product Unit of Measure',
        compute="_compute_total_qty",
        readonly=True,
        store=True,
    )
    deco_danger = fields.Boolean(
        compute="_compute_deco_danger"
    )

    @api.depends("unbuild_id.product_qty",
                # "unbuild_id.bom_id.bom_line_ids.product_qty",
                 "unbuild_id.bom_id.product_qty",)
    def _compute_expected_qty(self):
        # TODO inconsistent definition for expected_qty
        # (store=True, or @api.depends useless)
        for record in self.filtered("bom_line_id"):
            record.expected_qty = (
                record.bom_line_id.product_qty * record.unbuild_id.product_qty
            )

    def _compute_deco_danger(self):
        for record in self:
            # TODO replace it with properly float_is_zero call
            # as soon as possible
            if record.expected_qty == 0.0:
                record.deco_danger = (abs(record.total_qty) > 0.0)
            else:
                data = (
                    (record.total_qty - record.expected_qty) * 100
                    /
                    record.expected_qty
                )
                record.deco_danger = (abs(data) > 10)

    @api.onchange("unbuild_id.bom_quants_ids.custom_qty")
    @api.depends("unbuild_id.bom_quants_ids.custom_qty")
    def _compute_total_qty(self):
        for record in self:
            record.total_qty = 0
            for bom_quant in record.unbuild_id.bom_quants_ids.filtered(lambda x: x.bom_line_id.id == record.bom_line_id.id):
                record.total_qty += bom_quant.custom_qty

    def product_weighing(self):
        self.ensure_one()
        mrp_unbuild_bom = self.env.ref(
            "mrp_unbuild_bom_cust_qty.mrp_unbuild_bom_quants_view_form_extended"
        ).id
        qty = self.expected_qty - self.total_qty
        custom_qty = qty if qty > 0 else 0
        context = {
            'default_bom_line_id': self.bom_line_id.id,
            'default_unbuild_id': self.unbuild_id.id,
            'default_bom_id': self.unbuild_id.bom_id.id,
            'default_company_id': self.unbuild_id.company_id.id,
            'default_custom_qty':  custom_qty,
        }
        return {
            'name': _('Unbuild Bom'),
            'res_model': 'mrp.unbuild.bom.quants',
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': mrp_unbuild_bom,
            'target': 'new',
            'type': 'ir.actions.act_window',
            'context': context,
        }
