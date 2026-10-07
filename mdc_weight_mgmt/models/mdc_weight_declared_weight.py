# © 2026 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from datetime import timedelta


class MdcWeightDeclaredWeight(models.Model):
    _name = 'mdc.weight.declared.weight'
    _description = 'Declared Weight'

    product_id = fields.Many2one(
        comodel_name='product.product',
        string='Product',
        required=True
    )
    date_from = fields.Date(
        string='Date From',
        default=fields.Date.context_today,
    )
    date_to = fields.Date(
        string='Date To'
        )
    declared_weight = fields.Float(
        string='Declared Weight',
        )

    @api.constrains('date_from', 'date_to')
    def _check_dates(self):
        invalid = self.filtered(lambda r: r.date_from and r.date_to and r.date_to < r.date_from)
        if invalid:
            raise ValidationError(_("Date To cannot be before Date From."))

    def _check_overlap_manual(self, product_id, date_from, date_to, exclude_id=None):
        start = date_from or fields.Date.from_string('1900-01-01')
        end = date_to or fields.Date.from_string('9999-12-31')
        domain = [
            ('product_id', '=', product_id),
            '|', ('date_from', '=', False), ('date_from', '<=', end),
            '|', ('date_to', '=', False), ('date_to', '>=', start),
        ]
        if exclude_id:
            domain.append(('id', '!=', exclude_id))
        overlapping = self.search(domain, limit=1)
        if overlapping:
            return _(
                "Overlap detected with range %(start)s - %(end)s",
                start=overlapping.date_from,
                end=overlapping.date_to
            )
        return False

    def _check_gaps(self, product_id):
        records = self.search(
            [('product_id', '=', product_id)],
            order='date_from'
        )
        prev = None
        for rec in records:
            if prev and prev.date_to and rec.date_from:
                diff = (rec.date_from - prev.date_to).days
                if diff != 1:
                    raise ValidationError(
                        _("Gap detected between %s and %s") %
                        (prev.date_to, rec.date_from)
                    )
            prev = rec

    @api.model_create_multi
    def create(self, vals_list):
        vals_list_create = vals_list.copy()
        for vals in vals_list:
            product_id = vals.get('product_id')
            date_from = vals.get('date_from')
            date_to = vals.get('date_to')
            weight = vals.get('declared_weight')
            date_from_dt = fields.Date.to_date(date_from) if date_from else False
            current = self.search([
                ('product_id', '=', product_id),
                ('date_to', '=', False)
            ], limit=1)
            if current and date_from_dt and not date_to:
                if current.date_from == date_from_dt:
                    current.write({
                        'declared_weight': weight
                    })
                    vals_list_create.pop(vals_list.index(vals))
                    continue
                if current.declared_weight == weight:
                    raise ValidationError(
                        _("Same weight as current range, no new record needed")
                    )
                current.write({
                    'date_to': date_from_dt - timedelta(days=1)
                })
            msg = self._check_overlap_manual(product_id, date_from, date_to)
            if msg:
                raise ValidationError(msg)
        records = super().create(vals_list_create)
        for rec in records:
            self._check_gaps(rec.product_id.id)
        return records

    def write(self, vals_list):
        for rec in self:
            msg = self._check_overlap_manual(
                vals_list.get('product_id', rec.product_id.id),
                vals_list.get('date_from', rec.date_from),
                vals_list.get('date_to', rec.date_to),
                exclude_id=rec.id
            )
            if msg:
                raise ValidationError(msg)
            res = super().write(vals_list)
            for rec in self:
                self._check_gaps(rec.product_id.id)
            return res