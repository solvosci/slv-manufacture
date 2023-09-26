from odoo import api, fields, models, exceptions, _


class MdcConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    _name = 'mdc.config.settings'

    rfid_server_url = fields.Char('RFID Server URL')
    rfid_server_user = fields.Char('RFID Server User')
    rfid_server_password = fields.Char('RFID Server Password')
    rfid_ws_server_url = fields.Char('RFID WebSocket Server URL')
    rfid_server_min_secs_between_worksheets = fields.Char('RFID Server minimum seconds between worksheets')
    rfid_server_last_worksheet_timestamp = fields.Char('RFID Server last worksheet timestamp')
    lot_default_life_days = fields.Char('Lots default life in days')
    lot_last_total_gross_weight_update_timestamp = fields.Char('Lot last total gross weight update timestamp')
    data_win_cancel_mode = fields.Selection(
        selection=[('oneday', '1-day old'), ('yesterday', 'Yesterday'), ('fixedtime', 'Fixed time')],
        string="Input data cancel mode",
        help="""
        Selects how the input cancel cron will be perform the old unlinked inputs expiration:
        - 1-day old (default): when an input is 24 hours old or more
        - yesterday: when an input belongs to a previous day than today
        - fixedtime: input cancel cron runs only once a day at a fixed time 
                     and cancel all inputs without an output less than this fixed time
        """,
        default='oneday',
    )
    data_win_cancel_fixed_time = fields.Datetime(
        'Next date for input cancel cron and cancel inputs without an output less than this time'
    )
    rpt_hide_shift_change_data = fields.Boolean(
        'Hide shift change data in Reports',
        default=False
    )

    @api.model
    def get_values(self):
        res = super(MdcConfigSettings, self).get_values()
        IrConfigParameter = self.env['ir.config_parameter'].sudo()
        res.update(
            rfid_server_url=IrConfigParameter.get_param('mdc.rfid_server_url'),
            rfid_server_user=IrConfigParameter.get_param('mdc.rfid_server_user'),
            rfid_server_password=IrConfigParameter.get_param('mdc.rfid_server_password'),
            rfid_ws_server_url=IrConfigParameter.get_param('mdc.rfid_ws_server_url'),
            rfid_server_min_secs_between_worksheets=IrConfigParameter.get_param('mdc.rfid_server_min_secs_between_worksheets'),
            rfid_server_last_worksheet_timestamp=IrConfigParameter.get_param('mdc.rfid_server_last_worksheet_timestamp'),
            lot_default_life_days=IrConfigParameter.get_param('mdc.lot_default_life_days'),
            lot_last_total_gross_weight_update_timestamp=IrConfigParameter.get_param('mdc.lot_last_total_gross_weight_update_timestamp'),
            data_win_cancel_mode=IrConfigParameter.get_param('mdc.data_win_cancel_mode'),
            data_win_cancel_fixed_time=IrConfigParameter.get_param('mdc.data_win_cancel_fixed_time'),
            rpt_hide_shift_change_data=IrConfigParameter.get_param('mdc.rpt_hide_shift_change_data'),
        )
        return res

    @api.multi
    def set_values(self):
        super(MdcConfigSettings, self).set_values()

        if not self.user_has_groups('mdc.group_mdc_office_worker'):
            raise exceptions.UserError(_('You are not allowed to change this values'))
        try:
            min_secs = int(self.rfid_server_min_secs_between_worksheets)
        except ValueError as ve:
            raise models.ValidationError(_('The minimum seconds between worksheets must be an integer!!'))
        if min_secs <= 0:
            raise models.ValidationError(_('The minimum seconds between worksheets must be bigger than 0!!!'))

        try:
            lot_days = int(self.lot_default_life_days)
        except ValueError as ve:
            raise models.ValidationError(_('The lot default life days must be an integer!!'))
        if lot_days < 0:
            raise models.ValidationError(_('The lot default life days must be at least zero!!!'))

        IrConfigParameter = self.env['ir.config_parameter'].sudo()
        IrConfigParameter.set_param('mdc.rfid_server_url', self.rfid_server_url)
        IrConfigParameter.set_param('mdc.rfid_server_user', self.rfid_server_user)
        IrConfigParameter.set_param('mdc.rfid_server_password', self.rfid_server_password)
        IrConfigParameter.set_param('mdc.rfid_ws_server_url', self.rfid_ws_server_url)
        IrConfigParameter.set_param('mdc.rfid_server_min_secs_between_worksheets', self.rfid_server_min_secs_between_worksheets)
        IrConfigParameter.set_param('mdc.lot_default_life_days', self.lot_default_life_days)
        IrConfigParameter.set_param('mdc.data_win_cancel_mode', self.data_win_cancel_mode)
        IrConfigParameter.set_param('mdc.data_win_cancel_fixed_time', self.data_win_cancel_fixed_time)
        IrConfigParameter.set_param('mdc.rpt_hide_shift_change_data', self.rpt_hide_shift_change_data)
