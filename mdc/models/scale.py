# -*- coding: utf-8 -*-

import socket

from odoo import models, fields, api, _
from odoo.exceptions import UserError

# TODO make it CONST
SCALE_RECV_BUFFER_SIZE = 1024


class Scale(models.Model):
    '''
    Represents a Weighing Scale managed over TCP/IP
    '''
    _name = 'mdc.scale'
    _description = 'Weighing Scale'

    name = fields.Char(
        'Name',
        required=True,
        copy=False,
        default=_('New scale'))
    tcp_address_ip = fields.Char(
        'IP Address',
        required=True)
    tcp_address_port = fields.Integer(
        'IP Port',
        required=True)
    timeout_secs = fields.Integer(
        'Timeout (s)',
        required=True,
        default=5)
    scale_protocol = fields.Selection(
        [('$', '$ Protocol')],
        string='Weighing protocol',
        required=True,
        default='$')
    weight_uom_id = fields.Many2one(
        'product.uom',
        string='Weight Unit',
        required=True,
        domain="[('category_id','=',2)]")
    last_weight_value = fields.Float(
        'Last weight value',
        readonly=True,
        copy=False)
    last_weight_uom_id = fields.Many2one(
        'product.uom',
        string='Last weight Unit',
        readonly=True)
    last_weight_stability = fields.Selection(
        [('stable', 'Stable'), ('unstable', 'Unstable'), ('unknown', 'Unknown')],
        string='Last weight stability',
        readonly=True,
        copy=False)
    last_weight_datetime = fields.Datetime(
        'Last weight date',
        readonly=True,
        copy=False)
    # TODO waiting timeout
    active = fields.Boolean(
        'Active',
        default=True)
    # TODO current line

    # TODO ensure data validation (IP address,...) when creating and writing a record

    @api.multi
    def action_get_weight(self):
        '''
        Triggered by a form button, gets the current weight
        :return:
        '''
        self.ensure_one()
        try:
            self.get_weight()
            return True
        except Exception as err:
            raise UserError(err)

    def get_weight(self):
        '''
        Gets the current weight
        :return:
        '''
        # TODO waiting timeout
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(self.timeout_secs)
            s.connect((self.tcp_address_ip, self.tcp_address_port))
            if self.scale_protocol == '$':
                """
                self.last_weight_value, self.last_weight_stability, self.last_weight_datetime \
                    = self._get_weight_s_protocol(s)
                """
                t_last_weight_value, t_last_weight_stability, t_last_weight_datetime \
                    = self._get_weight_s_protocol(s)
            else:
                raise Exception(_('Unsupported weighing protocol (%s)') % self.protocol)
            # self.last_weight_uom_id = self.weight_uom_id
            """
            return self.last_weight_value, self.last_weight_uom_id, \
                self.last_weight_stability, self.last_weight_datetime
            """
            return t_last_weight_value, self.weight_uom_id, \
                   t_last_weight_stability, t_last_weight_datetime

    def _get_weight_s_protocol(self, sock):
        sock.send(b'$')
        data = sock.recv(SCALE_RECV_BUFFER_SIZE)
        # STX = 0x02 , ETX = 0x0D ; other control data is not set
        if len(data) == 11 and data[0] == 0x02 and data[-1] == 0x0D:
            weight = float(data[2:-1])
            stability = 'stable' if '{0:b}'.format(data[1])[-6] == '0' else 'unstable'
            return weight, stability, fields.Datetime.now()
        else:
            raise UserError(_('Unknown data format. Data received: %s') % data)
