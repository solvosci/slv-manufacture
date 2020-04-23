from odoo import api, fields, models
from odoo.addons.base.res.res_partner import _tz_get


class MdcConfigSettings(models.TransientModel):
    _inherit = 'mdc.config.settings'

    rpt_physical_worksheet_timezone = fields.Selection(
        _tz_get,
        string='Physical Worksheet Report default timezone',
        default=lambda self: self._context.get('tz'))

    @api.model
    def get_values(self):
        res = super(MdcConfigSettings, self).get_values()
        IrConfigParameter = self.env['ir.config_parameter'].sudo()
        res.update(
            rpt_physical_worksheet_timezone=IrConfigParameter.get_param(
                'mdc_rpt_physical_worksheet.rpt_physical_worksheet_timezone'),
        )
        return res

    @api.multi
    def set_values(self):
        super(MdcConfigSettings, self).set_values()
        IrConfigParameter = self.env['ir.config_parameter'].sudo()
        IrConfigParameter.set_param(
            'mdc_rpt_physical_worksheet.rpt_physical_worksheet_timezone',
            self.rpt_physical_worksheet_timezone)
