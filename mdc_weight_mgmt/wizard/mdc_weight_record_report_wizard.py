# © 2025 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html
from odoo import models, fields, api, _
from odoo.tools import float_is_zero
from odoo.exceptions import UserError, ValidationError
import pytz

class MdcWeightRecordReportWizard(models.TransientModel):
    _name = 'mdc.weight.record.report.wizard'
    _description = 'Weight record report wizard'

    company_id = fields.Many2one(
        comodel_name="res.company",
        default=lambda self: self.env.company
    )
    mdc_weight_record_ids = fields.Many2many(
        comodel_name="mdc.weight.record",
        compute="_compute_mdc_weight_record_ids"
    )
    weight_uom = fields.Many2one(
        comodel_name="uom.uom",
        compute="_compute_mdc_weight_record_ids"
    )
    date_from = fields.Date(
        string="Start Date",
        required=True
    )
    date_to = fields.Date(
        string="End Date",
        required=True,
    )
    shift_id = fields.Many2one(
        comodel_name="mdc.weight.shift",
        string="Shift",
    )
    equipment_id = fields.Many2one(
        comodel_name="maintenance.equipment",
        string="Equipment",
        required=False,
        domain=lambda self: self._get_equipment_domain()
    )
    product_ids = fields.Many2many(
        comodel_name="product.product",
        string="Products",
        required=False,
        domain=lambda self: self._get_product_domain()
    )

    @api.constrains('date_from', 'date_to')
    def _check_dates(self):
        for record in self:
            if record.date_from and record.date_to and record.date_to < record.date_from:
                raise ValidationError(_("The end date must be later than the start date."))

    @api.depends('company_id')
    def _get_product_domain(self):
        product_categ_default_id = self.env.company.product_categ_default_id

        if product_categ_default_id:
            categories = self.env['product.category'].search([
                ('complete_name', 'like', product_categ_default_id.complete_name + '%')
            ])
            categ_ids = categories.ids if categories else []
            return [('categ_id', 'in', categ_ids)] if categ_ids else []
        return []

    @api.depends('company_id')
    def _get_equipment_domain(self):
        equipment_category_default_id = self.env.company.equipment_category_default_id

        if equipment_category_default_id:
            return [('category_id', '=', equipment_category_default_id.id)]
        return []

    @api.depends('date_from', 'date_to', 'shift_id','equipment_id','product_ids')
    def _compute_mdc_weight_record_ids(self):
        for record in self:
            if record.date_from and record.date_to:
                domain = [
                    ('start', '>=', record.date_from),
                    ('end', '<=', record.date_to),
                ]
                if record.equipment_id:
                    domain += [('equipment_id', '=', record.equipment_id.id)]
                if record.product_ids:
                    domain.append(('product_id', 'in', record.product_ids.ids))

                matched_records = []
                all_records = self.env['mdc.weight.record'].search(domain)

                if record.shift_id:
                    shift_from = record.shift_id.hour_from
                    shift_to = record.shift_id.hour_to
                    user_tz = self.env.context.get('tz') or self.env.user.tz

                    for weight_record in all_records:
                        # Convert start time to user's timezone to compare with shift times
                        start_dt = pytz.utc.localize(weight_record.start).astimezone(pytz.timezone(user_tz))
                        start_hour = start_dt.hour + start_dt.minute / 60.0
                        if shift_from < shift_to:
                            if shift_from <= start_hour < shift_to:
                                matched_records.append(weight_record.id)
                else:
                    matched_records = all_records.ids
                if matched_records:
                    record.mdc_weight_record_ids = [(6, 0, matched_records)]
                    record.weight_uom = record.mdc_weight_record_ids[0].weight_uom
                else:
                    record.mdc_weight_record_ids = False
                    record.weight_uom = False
            else:
                record.mdc_weight_record_ids = False
                record.weight_uom = False

    def _validate_report_data(self):
        if not self.mdc_weight_record_ids:
            raise UserError(_("There is no records for that day, shift, equipment or product."))

    def action_mdc_weight_report_html(self):
        self._validate_report_data()
        return self.env.ref('mdc_weight_mgmt.action_mdc_weight_report_html').report_action(self)

    def action_mdc_weight_report_pdf(self):
        self._validate_report_data()
        return self.env.ref('mdc_weight_mgmt.action_mdc_weight_report_pdf').report_action(self)

    def sum_total(self, records, key):
        return sum(getattr(record, key)for record in records)

    def total_avg(self, unit_a, unit_b):
        if float_is_zero(unit_b, precision_digits=2):
            return 0.0
        return unit_a/unit_b

    def total_pct_avg(self, unit_a, unit_b):
        if float_is_zero(unit_b, precision_digits=2):
            return 0.0
        return (unit_a/unit_b) * 100

    def total_weight_nom(self, records):
        total_unit_ok = self.sum_total(records, 'unit_ok')
        if float_is_zero(total_unit_ok, precision_digits=2):
            return 0.0
        sum_weight_nom = 0
        for record in records:
            sum_weight_nom += record.weight_nom_qty * record.unit_ok
        return sum_weight_nom / total_unit_ok
