from odoo import api, fields, models
from odoo.addons.base.res.res_partner import _tz_get


class MdcConfigSettings(models.TransientModel):
    _inherit = 'mdc.config.settings'

    last_data_wout_gross_weight_rev_cron = fields.Datetime(
        'Next date for gross weight revision cron'
    )

    @api.model
    def get_values(self):
        res = super(MdcConfigSettings, self).get_values()
        IrConfigParameter = self.env['ir.config_parameter'].sudo()
        res.update(
            last_data_wout_gross_weight_rev_cron=IrConfigParameter.get_param(
                'last_data_wout_gross_weight_revision'
                '.last_data_wout_gross_weight_rev_cron'),
        )
        return res

    @api.multi
    def set_values(self):
        super(MdcConfigSettings, self).set_values()
        IrConfigParameter = self.env['ir.config_parameter'].sudo()
        IrConfigParameter.set_param(
            'last_data_wout_gross_weight_revision'
            '.last_data_wout_gross_weight_rev_cron',
            self.last_data_wout_gross_weight_rev_cron)
