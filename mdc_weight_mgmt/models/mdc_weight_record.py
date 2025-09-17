# © 2025 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html
import pytz
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class MdcWeightRecord(models.Model):
    _name= 'mdc.weight.record'
    _description = 'Weight record'
    _order = 'id desc'

    name = fields.Char(
        compute="_compute_name"
    )
    product_id = fields.Many2one(
        comodel_name='product.product',
        string='Product',
        required=True,
        domain=lambda self: self._get_product_domain()
    )

    equipment_id = fields.Many2one(
        comodel_name='maintenance.equipment',
        string='Equipment',
        required=True,
        domain=lambda self: self._get_equipment_domain()
    )

    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company
    )
    weight_uom = fields.Many2one(
        comodel_name='uom.uom',
        string='UOM type',
        required=True,
        default=lambda self: self.env.ref('uom.product_uom_gram').id
    )
    weight_total_uom = fields.Many2one(
        comodel_name='uom.uom',
        string='UOM type for total',
        required=True,
        default=lambda self: self.env.ref('uom.product_uom_kgm').id
    )
    weight_nom_qty = fields.Float(
        string='Nominal Weight',
        required=True
    )
    weight_dec_qty = fields.Float(
        string='Declared Weight',
        required=True
    )
    start = fields.Datetime(
        string='Start register date',
        required=True
    )
    end = fields.Datetime(
        string='End register date',
        required=True
    )
    period_min = fields.Float(
        string="Period (min)",
    )
    unit_total = fields.Integer(
        string='Total Units',
        compute='_compute_unit_total'
        )
    unit_x_min = fields.Float(
        string='Units per minute',
        compute='_compute_unit_x_min',
    )
    unit_reject_exceed = fields.Integer(
        string="Units rejected overweight",
        help='Units rejected due to exceed overweight'
    )
    unit_reject_low = fields.Integer(
        string="Units rejected low weight",
        help='Units rejected due to low weight'
    )
    unit_reject_total = fields.Integer(
        string='Total units rejected',
        compute='_compute_unit_reject_total',
        store=True
    )
    unit_reject_pct = fields.Float(
        string='Units rejected (%)',
        compute='_compute_unit_reject_pct',
    )
    unit_ok = fields.Integer(
        string='Units accepted',
    )
    unit_ok_pct = fields.Float(
        string='Units accepted (%)',
        compute='_compute_unit_ok_pct',
    )
    weight_ok_tot_qty = fields.Float(
        string='Total weight accepted'
    )
    weight_ok_dec_qty = fields.Float(
        string='Total weight declared',
        compute='_compute_weight_ok_dec_qty',
    )
    weight_ok_avg_qty = fields.Float(
        string='Average weight accepted',
        compute='_compute_weight_ok_avg_qty',
    )
    exceed_pct = fields.Float(
        string='Excess weight (%)',
        compute='_compute_exceed_pct',
    )

    def _get_product_domain(self):
        product_categ_default_id = self.env.company.product_categ_default_id

        if product_categ_default_id:
            categories = self.env['product.category'].search([
                ('id', 'child_of', product_categ_default_id.id)
            ])
            if categories.ids:
                return [('categ_id', 'in', categories.ids)]
        return []

    def _get_equipment_domain(self):
        equipment_category_default_id = self.env.company.equipment_category_default_id

        if equipment_category_default_id:
            return [('category_id', '=', equipment_category_default_id.id)]
        return []

    def write(self, vals):
        res = super(MdcWeightRecord, self).write(vals)
        for record in self:
            new_start = vals.get('start', record.start)
            new_end = vals.get('end', record.end)
            if isinstance(new_start, str):
                new_start = fields.Datetime.from_string(new_start)
            if isinstance(new_end, str):
                new_end = fields.Datetime.from_string(new_end)
            if new_end < new_start:
                raise ValidationError(_("The end date must be later than the start date."))
        return res

    @api.constrains('equipment_id', 'start', 'end')
    def _check_overlap_constrains(self):
        for record in self:
            if not record.equipment_id or not record.start or not record.end or self.env.context.get('mdc_cron_create', False):
                continue
            msg = self._check_overlap_manual(record.equipment_id, record.start, record.end)
            if msg:
                raise ValidationError(msg)

    @api.model
    def _check_overlap_manual(self, equipment_id, start, end):
        overlapping = self.search([
            ('equipment_id', '=', equipment_id.id),
            '|',
                '&', ('start', '<=', start), ('end', '>', start),
                '&', ('start', '<', end),   ('end', '>=', end),
        ], limit=1)
        if overlapping:
            return (_(
                "There is already a record with this equipment (%(equipment)s) at this time range: %(start)s - %(end)s",
                equipment=equipment_id.name,
                start=start,
                end=end
            ))
        return False

    def convert_weight(self, weight_value, weight_uom_from, weight_uom_to):
        self.ensure_one()
        return weight_uom_from._compute_quantity(weight_value, weight_uom_to)

    @api.depends('product_id','equipment_id','start','end')
    def _compute_name(self):
        for record in self:
            product_name = record.product_id.name or ''
            equipment_name = record.equipment_id.name or ''
            record.name = f"{product_name} - {equipment_name} - {record.start} UTC - {record.end} UTC"

    def _compute_unit_total(self):
        for record in self:
            record.unit_total = record.unit_ok + record.unit_reject_total

    def _compute_period_min(self):
        for record in self:
            if record.start and record.end:
                record.period_min = (record.end - record.start).total_seconds() / 60 
            else:
                record.period_min = 0

    def _compute_unit_x_min(self):
        for record in self:
            if record.period_min:
                record.unit_x_min = record.unit_total / record.period_min
            else:
                record.unit_x_min = 0

    @api.depends('unit_reject_exceed','unit_reject_low')
    def _compute_unit_reject_total(self):
        for record in self:
            record.unit_reject_total = record.unit_reject_exceed + record.unit_reject_low

    def _compute_unit_reject_pct(self):
        for record in self:
            if record.unit_total:
                record.unit_reject_pct = (record.unit_reject_total / record.unit_total) * 100
            else:
                record.unit_reject_pct = 0

    @api.depends('unit_total','unit_reject_total')
    def _compute_unit_ok(self):
        for record in self:
            record.unit_ok = record.unit_total - record.unit_reject_total

    def _compute_unit_ok_pct(self):
        for record in self:
            if record.unit_total:
                record.unit_ok_pct = (record.unit_ok / record.unit_total) * 100
            else:
                record.unit_ok_pct = 0

    def _compute_weight_ok_dec_qty(self):
        for record in self:
            record.weight_ok_dec_qty = record.convert_weight((record.weight_dec_qty * record.unit_ok),record.weight_uom,record.weight_total_uom)

    def _compute_weight_ok_avg_qty(self):
        for record in self:
            if record.unit_ok:
                record.weight_ok_avg_qty = record.convert_weight((record.weight_ok_tot_qty / record.unit_ok),record.weight_total_uom,record.weight_uom)
            else:
                record.weight_ok_avg_qty = 0

    def _compute_exceed_pct(self):
        for record in self:
            if record.weight_nom_qty and record.weight_ok_avg_qty:
                record.exceed_pct = ((record.weight_ok_avg_qty - record.weight_nom_qty )/ record.weight_nom_qty) * 100
            else:
                record.exceed_pct = 0

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None,orderby=False, lazy=True):
        res = super(MdcWeightRecord, self).read_group(domain, fields, groupby,offset=offset, limit=limit, orderby=orderby, lazy=lazy)
        group_fields = ['unit_ok_pct', 'exceed_pct', 'weight_ok_avg_qty']
        if any([x in fields for x in group_fields]):
            for line in res:
                if '__domain' in line:
                    unit_ok_pct_avg = 0
                    exceed_pct_avg = 0
                    weight_ok_avg_qty_avg = 0
                    total = 0
                    lines = self.search(line['__domain'])
                    for line_item in lines:
                        unit_ok_pct_avg += line_item.unit_ok_pct
                        exceed_pct_avg += line_item.exceed_pct
                        weight_ok_avg_qty_avg += line_item.weight_ok_avg_qty
                        total += 1
                    if total > 0:
                        line['unit_ok_pct'] = unit_ok_pct_avg / total
                        line['exceed_pct'] = exceed_pct_avg / total
                        line['weight_ok_avg_qty'] = weight_ok_avg_qty_avg / total
        return res
