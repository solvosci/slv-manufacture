# © 2022 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html

import socket
from odoo import models, fields, _
from odoo.exceptions import UserError

class FCDCheckpoint(models.Model):
    _name = 'fcd.checkpoint'
    _description = 'Weighting Data'

    name = fields.Char(string='Name')
    scale_id = fields.Many2one('fcd.weight.scale')
    allowed_ip = fields.Char()
    warehouse_id = fields.Many2one('stock.warehouse')

    def _default_date(self):
        return fields.Datetime.now()

    def get_weight(self, values):
        chkpoint = self.env['fcd.checkpoint'].browse(int(values['chkpoint_id']))
        if not chkpoint:
            raise UserError(_('Checkpoint #%s not found') % values['chkpoint_id'])
        if not chkpoint.scale_id:
            raise UserError(_("Scale not defined"))
        try:
            weight_value, weight_uom_id, weight_stability = chkpoint.scale_id.get_weight()[0:3]
        except socket.timeout:
            raise UserError(_("Timed out on weighing scale"))

        # if weight_stability == 'unstable':
        #     raise UserError(_('Unstable %.2f %s weight was read. Please slide the card one more time') %
        #                     (weight_value, weight_uom_id.name))

        if values.get("tare"):
            weight_value = weight_value - float(values['tare'])

        return {'weight_value': '%.2f' % weight_value}
            