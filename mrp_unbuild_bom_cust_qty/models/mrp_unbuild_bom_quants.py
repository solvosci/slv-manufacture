# © 2021 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (http://www.gnu.org/licenses/lgpl-3.0.html)

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class MrpUnbuildBoMQuants(models.Model):
    _name = "mrp.unbuild.bom.quants"
    _inherit = "mrp.unbuild.bom.mixin"
    _description = "Quants for BoM based Unbuild"

    custom_qty = fields.Float(
        string="Quantity",
        digits='Product Unit of Measure',
        required=True,
    )
    departure_date = fields.Datetime(
        readonly=True
    )

    @api.constrains("custom_qty")
    def _check_custom_qty(self):
        for record in self:
            if record.custom_qty <= 0.0:
                raise ValidationError(
                    _("Invalid quant for %s: it must be greater than zero!") %
                    record.name
                )

    def save_and_new(self):
        self.ensure_one()
        mrp_unbuild_bom = self.env.ref(
            "mrp_unbuild_bom_cust_qty.mrp_unbuild_bom_quants_view_form_extended"
        ).id
        context = {
            'default_bom_line_id': self.bom_line_id.id,
            'default_unbuild_id': self.unbuild_id.id,
            'default_bom_id': self.unbuild_id.bom_id.id,
            'default_company_id': self.unbuild_id.company_id.id,
            'default_custom_qty':  0.0,
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

    def save_and_close(self):
        self.ensure_one()
        return {'type': 'ir.actions.act_window_close'}

    @api.model
    def create(self, vals_list):
        res = super().create(vals_list)
        res.departure_date = fields.datetime.now()
        res.name = ('%s on %s at %s' % (self.env.user.name,
                                        fields.datetime.now().strftime('%d/%m/%Y'),
                                        fields.datetime.now().strftime('%H:%M')))
        return res
