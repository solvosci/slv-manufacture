import socket
from odoo import models, fields, api, _
from odoo.http import request
from odoo.exceptions import UserError, AccessError

class weight_scale(models.Model):
    _name = 'weight.scale.chkpoint'
    _description = 'Weighting Data'

    # Get values
    def _default_date(self):
        return fields.Datetime.now()

    # Create model propertyes

    chkpoint_id = fields.Many2one(
        'weight_scale.chkpoint',
        string='Checkpoint',
        required=True)
    current_lot_active_id = fields.Many2one(
        'weight_scale.lot',
        string='Current Lot Active Id')
    start_lot_datetime = fields.Datetime(
        string = 'Start MO Active date time')

    @api.onchange('current_lot_active_id')
    def _onchange_current_lot_active_id(self):
        now = fields.Datetime.now()
        for reg in self:
            reg.start_lot_datetime = now
    
    @api.onchange('start_lot_datetime')
    def _onchange_start_lot_datetime(self):
        now = fields.Datetime.now()
        for reg in self:
            if reg.start_lot_datetime and reg.start_lot_datetime > now:
                raise UserError(_('You can´t establish a future datetime'))

    


    # lot_id = fields.Many2one(
    #     'producto.product',
    #     string='MO',
    #     required=True)
    # product_id = fields.Many2one(
    #     'product.product',
    #     string='MO',
    #     required=True)
    # weight = fields.Float(
    #     'Weight')
    # w_uom_id = fields.Many2one(
    #     'product.product',
    #     string='Weight UoM',
    #     required=True)


    # Get weight
    def packaging_lot(self, vals):
        chkpoint = self.env['mdc.chkpoint'].browse(vals['chkpoint_id'])
        # Get weight
        try:
            weight_value, weight_uom_id, weight_stability = chkpoint.scale_id.get_weight()[0:3]
        except socket.timeout:
            return {'error' : _("Timed out on weighing scale")}

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
