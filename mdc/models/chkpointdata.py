# -*- coding: utf-8 -*-

import datetime as dt
import logging
import socket
from odoo import api, models, fields, _
from odoo.exceptions import UserError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DF

_logger = logging.getLogger(__name__)


class DataWIn(models.Model):
    """
    Main data for a chkpoint_datacapture weight input
    """
    _name = 'mdc.data_win'
    _description = 'Weight Input Data'

    def _default_date(self):
        #return fields.Datetime.from_string(fields.Datetime.now())
        return fields.Datetime.now()

    def _get_card_id_domain(self):
        # TODO add filter "card is not in use"
        return [('card_categ_id', '=', self.env.ref('mdc.mdc_card_categ_P').id)]

    def _default_uom(self):
        return self.env.ref('product.product_uom_kgm')
    def _get_w_uom_id_domain(self):
        return [('category_id', '=', self.env.ref('product.product_uom_categ_kgm').id)]

    line_id = fields.Many2one(
        'mdc.line',
        string='Line',
        required=True)
    lot_id = fields.Many2one(
        'mdc.lot',
        string='MO',
        required=True)
    create_datetime = fields.Datetime(
        'Datetime',
        required=True,
        default=_default_date)
    tare = fields.Float(
        'Tare',
        required=True)
    weight = fields.Float(
        'Weight',
        default=0,
        required=True)
    w_uom_id = fields.Many2one(
        'product.uom',
        string='Weight UoM',
        required=True,
        domain=_get_w_uom_id_domain,
        default=_default_uom)
    card_id = fields.Many2one(
        'mdc.card',
        string='Card',
        required=True,
        domain=_get_card_id_domain)
    wout_id = fields.Many2one(
        'mdc.data_wout',
        string='WOut')
    cancel_user_id = fields.Many2one(
        'res.users',
        string='Cancelled by')
    cancel_datetime = fields.Datetime(
        'Cancel date')
    active = fields.Boolean(
        'Active',
        default=True)

    @api.model
    def create(self, values):
        data_win_card = self.search([('wout_id', '=', False), ('card_id', '=', values['card_id'])])
        if data_win_card:
            raise UserError(_('There is already open data with the selected card (%s)') % data_win_card[0].card_id.name)

        return super(DataWIn, self).create(values)

    def from_cp_create(self, values):
        '''
        Saves a checkpoint entry from some input data
        '''

        # Data received:
        # - checkpoint_id.id
        # - card_code

        chkpoint = self.env['mdc.chkpoint'].browse(values['chkpoint_id'])
        if not chkpoint:
            raise UserError(_('Checkpoint #%s not found') % values['chkpoint_id'])
        if not chkpoint.current_lot_active_id:
            raise UserError(_("There's not an active lot"))
        if not chkpoint.scale_id:
            raise UserError(_("Scale not defined"))
        if not chkpoint.tare_id:
            raise UserError(_("Tare not defined"))
        try:
            weight_value, weight_uom_id, weight_stability = chkpoint.scale_id.get_weight()[0:3]
        except socket.timeout:
            raise UserError(_("Timed out on weighing scale"))

        if weight_stability == 'unstable':
            raise UserError(_('Unstable %.2f %s weight was read. Please slide the card one more time') %
                            (weight_value, weight_uom_id.name))

        card = self.env['mdc.card'].search([('name', '=', values['card_code'])])
        if not card:
            raise UserError(_("Card #%s not found") % values['card_code'])
        if card.card_categ_id.id != self.env.ref('mdc.mdc_card_categ_P').id:
            raise UserError(_("Invalid Card #%s") % values['card_code'])

        return self.create({
            'line_id': chkpoint.line_id.id,
            'lot_id': chkpoint.current_lot_active_id.id,
            'tare': chkpoint.tare_id.tare,
            'weight': weight_value,
            'w_uom_id': weight_uom_id.id,
            'card_id': card.id
        })

    @api.multi
    def cancel_input(self):
        """
        Cancels (if possible) the current input data
        :return:
        """
        # Since this model has special rule access, this action is guaranteed
        #  for that users allowed to reach this action
        wins = self.sudo().browse(self.ids)
        for w in wins:
            if w.wout_id:
                raise UserError(_("Cannot cancel input '%s - %s - %s' because it's been already linked with an output")
                                % (w.line_id.name, w.lot_id.name, w.create_datetime))
            w.write({
                'active': False,
                'cancel_user_id': self.env.user.id,
                'cancel_datetime': fields.Datetime.now()})
            _logger.info('[mdc.data_win] Cancelled input %s - %s - %s' % (w.line_id.name, w.lot_id.name, w.create_datetime))

    def get_average_data(self, context):
        """
        Obtains average data for the given context (e.g. line_id and lot_id)
        """
        w_create_datetime = None
        w_tare = None
        w_uom_id = None
        w_weight = 0
        w_numwin = 0
        w_timewout = 0
        w_numwout = 0
        win_lots = self.search([('line_id', '=', context['line_id']), ('lot_id', '=', context['lot_id'])],
                               order='create_datetime asc')
        if win_lots:
            for wi in win_lots:
                if w_tare is None:
                    w_tare = wi.tare
                    w_uom_id = wi.w_uom_id.id
                # if we don´t find any wout we have the first create_datetime
                if w_create_datetime is None:
                    w_create_datetime = wi.create_datetime
                # just keep in mind records with the same tare
                if wi.tare == w_tare and wi.w_uom_id.id == w_uom_id:
                    w_weight += wi.weight
                    w_numwin += 1
                    _logger.info('[mdc.data_win] _calculate_lot_average_data WIN %s - weight: %s ' %
                                 (w_numwin, wi.weight))
                # to calculate create_datetime we need the create_datetime of the wout
                if wi.wout_id is not None:
                    # retrieve the wout record
                    wo = self.env['mdc.data_wout'].browse(wi.wout_id.id)
                    if wo:
                        w_numwout += 1
                        difference = dt.datetime.strptime(wo.create_datetime, '%Y-%m-%d %H:%M:%S') - \
                                     dt.datetime.strptime(wi.create_datetime, '%Y-%m-%d %H:%M:%S')
                        dif_hours = difference.days * 24 + difference.seconds / 3600
                        w_timewout += dif_hours
                        _logger.info(
                            '[mdc.data_win] get_average_data WOUT %s - datetime_in: %s - datetime_out: %s - diff.: %s'
                            % (w_numwout, wi.create_datetime, wo.create_datetime, dif_hours))
        else:
            _logger.error(
                '[mdc.data_win] get_average_data not '
                'found for line_id=%s and lot_id=%s' %
                (context['line_id'], context['lot_id']))

        # calculate de average of the weight
        if w_numwin > 0:
            w_weight = w_weight / w_numwin
        # calculate de average of the timewout
        # if we don´t find any wout we have the first create_datetime
        if w_numwout > 0:
            w_timewout = w_timewout / w_numwout
            ww_create_datetime = dt.datetime.now() - dt.timedelta(hours=w_timewout)
            w_create_datetime = ww_create_datetime.strftime("%Y-%m-%d %H:%M:%S")

        # return data to create de joker win reg
        _logger.info('[mdc.data_win] _calculate_lot_average_data to lot id %s and line id %s: '
                     'avg_time: %s - numwout: % s - create_datetime: %s - '
                     'numwin:%s - tare: %s - weight: %s - uom: %s'
                     % (context['lot_id'], context['line_id'], w_timewout, w_numwout, w_create_datetime, w_numwin,
                        w_tare, w_weight, w_uom_id))
        return w_tare and {
            'create_datetime': w_create_datetime or fields.Datetime.now(),
            'tare': w_tare,
            'weight': w_weight,
            'w_uom_id': w_uom_id
        }

    def _cancel_expired_inputs(self):
        """
        Cancels all the inputs created at least a day ago and not yet linked with an output
        :return:
        """
        data_win_cancel_mode = self.env['ir.config_parameter'].sudo().get_param(
            'mdc.data_win_cancel_mode'
        )
        expiration_date = dt.datetime.now() + dt.timedelta(days=-1) 
        if data_win_cancel_mode == 'yesterday':
            expiration_date = expiration_date.replace(hour=23, minute=59, second=59)
        if data_win_cancel_mode == 'fixedtime':
            next_datetime_cron = self.env['ir.config_parameter'].sudo().get_param(
                'mdc.data_win_cancel_fixed_time'
            )
            if fields.Datetime.to_string(dt.datetime.now()) < next_datetime_cron:
                return
            expiration_date = fields.Datetime.from_string(next_datetime_cron)
        cancellable_inputs = self.search([('wout_id', '=', False),
                                          ('create_datetime', '<=', fields.Datetime.to_string(expiration_date))])
        if cancellable_inputs:
            try:
                cancellable_inputs.cancel_input()
            except UserError as e:
                _logger.error('[mdc.data_win] _cancel_expired_inputs:  %s' % e)

        if data_win_cancel_mode == 'fixedtime':
            # update next execution date
            next_datetime_cron = expiration_date + dt.timedelta(days=1)
            self.env['ir.config_parameter'].sudo().set_param(
                'mdc.data_win_cancel_fixed_time',
                next_datetime_cron)

    def count_nreg(self, line_id, start_change_interval, end_change_interval):
        numReg = self.search_count(
             ['&', '&', ('line_id', '=', line_id.id),
              ('create_datetime', '>=', start_change_interval), ('create_datetime', '<', end_change_interval)])
        _logger.info("data_win count_nreg (%s): line_id: %s, start_change_interval: %s, end_change_interval: %s."
                     % (numReg, line_id.id, start_change_interval, end_change_interval))
        return numReg


class DataWOut(models.Model):
    """
    Main data for a chkpoint_datacapture weight input
    """
    _name = 'mdc.data_wout'
    _description = 'Weight Output Data'

    def _default_date(self):
        #return fields.Datetime.from_string(fields.Datetime.now())
        return fields.Datetime.now()

    def _default_uom(self):
        return self.env.ref('product.product_uom_kgm')
    def _get_w_uom_id_domain(self):
        return [('category_id', '=', self.env.ref('product.product_uom_categ_kgm').id)]

    line_id = fields.Many2one(
        'mdc.line',
        string='Line',
        required=True)
    lot_id = fields.Many2one(
        'mdc.lot',
        string='MO',
        required=True)
    create_datetime = fields.Datetime(
        'Datetime',
        required=True,
        default=_default_date)
    tare = fields.Float(
        'Tare',
        required=True)
    weight = fields.Float(
        'Weight',
        default=0,
        required=True)
    w_uom_id = fields.Many2one(
        'product.uom',
        string='Weight UoM',
        required=True,
        domain=_get_w_uom_id_domain,
        default=_default_uom)
    quality_id = fields.Many2one(
        'mdc.quality',
        string='Quality',
        required=True)
    card_ids = fields.Many2many(
        'mdc.card',
        string='Card')
    workstation_id = fields.Many2one(
        'mdc.workstation',
        string='Workstation',
        required=True)
    shift_id = fields.Many2one(
        'mdc.shift',
        string='Shift',
        required=True)
    employee_id = fields.Many2one(
        'hr.employee',
        string='Employee',
        required=True)
    shared = fields.Boolean(
        string='Shared',
        default=False)
    wout_shared_id =fields.Many2one(
        'mdc.data_wout',
        string='Shared with')
    wout_categ_id = fields.Many2one(
        'mdc.wout_categ',
        string='Out Category',
        required=True)
    gross_weight = fields.Float(
        'Gross Weight',
        readonly=True,
        default=0)

    @api.onchange('card_ids')
    def _retrieve_workstation_card_data(self):

        for dataWOut in self:
            #search workstation card
            for card_id in dataWOut.card_ids:
                card = self.env['mdc.card'].search([('id', '=', card_id.id), ('workstation_id', '!=', False)])
                if card:
                    dataWOut.workstation_id = card.workstation_id.id
                    dataWOut.shift_id = card.workstation_id.shift_id.id
                    dataWOut.employee_id = card.workstation_id.current_employee_id.id

    @api.multi
    def name_get(self):
        res = []
        for rec in self:
            res.append((rec.id, str(rec.id)))
        return res

    @api.model
    def create(self, values):
        gross_weight = 0.0

        #retrive all card ids
        card_ids = [] if len(values.get('card_ids')) == 0 else values.get('card_ids')[0][2]

        #var to store data_win ids of cards
        ids_win = []
        current_lot_id = None

        # For further validations
        workstation_card = None

        if len(card_ids) > 0:
            cards = self.env['mdc.card'].browse(card_ids)
            for card in cards:
                # Product card
                if card.card_categ_id.id == self.env.ref('mdc.mdc_card_categ_P').id:
                    data_win = self.env['mdc.data_win'].search([('card_id', '=', card.id), ('wout_id', '=', False)])
                    if data_win:
                        if len(data_win) > 1:
                            raise UserError(_('Card #%s is associated with inputs %s. Please cancel one of them')
                                            % (card.name, data_win.mapped('id')))
                        if current_lot_id and current_lot_id.id != data_win.lot_id.id:
                            raise UserError(_("Card #%s comes from a different lot (current: %s)") %
                                            (card.name, current_lot_id.name))
                        current_lot_id = data_win.lot_id
                        gross_weight += data_win.weight - data_win.tare
                        ids_win.append(data_win.id)
                    else:
                        raise UserError(_("Card #%s not valid: there's not open input data linked with") % card.name)
                # Workstation card
                elif card.card_categ_id.id == self.env.ref('mdc.mdc_card_categ_L').id:
                    if workstation_card:
                        raise UserError(_("Only one workstation card is allowed"))
                    if card.workstation_id.current_employee_id:
                        values['employee_id'] = card.workstation_id.current_employee_id.id
                    else:
                        raise UserError(_("Card #%s not valid: there's not any employee assigned with") % card.name)
                    values['workstation_id'] = card.workstation_id.id
                    values['shift_id'] = card.workstation_id.shift_id.id
                    workstation_card = card
                elif card.card_categ_id.id == self.env.ref('mdc.mdc_card_categ_PC').id:
                    # Joker card. Prior to create the output we should make a related input
                    # Conventions:
                    # - There isn't lot validation (we take the output one)
                    # FIXME Tare: WOUT checkpoint tare, not the WIN one! Should associate a tare with every joker card?
                    # - weight: the current average for the lot
                    # FIXME w_uom_id: we don't know how to fill, then we take the WOUT scale
                    """
                    joker_win = self.env['mdc.data_win'].create({
                        'line_id': values['line_id'],
                        'lot_id': values['lot_id'],
                        'tare': values['tare'],
                        'weight': self.env['mdc.lot'].browse(values['lot_id']).get_input_avg_weight(),
                        'w_uom_id': values['w_uom_id'],
                        'card_id': card.id
                    })
                    """
                    joker_win_data = self.env['mdc.data_win'].get_average_data({
                        'lot_id': values['lot_id'], 'line_id': values['line_id']})
                    if not joker_win_data:
                        joker_card_lot = \
                            self.env['mdc.lot'].browse(values['lot_id'])
                        raise UserError(_(
                            "Invalid joker card #%s. Before using it, "
                            "please make at least an input for this line "
                            "with lot %s") % (card.name, joker_card_lot.name))
                    joker_win_data['lot_id'] = values['lot_id']
                    joker_win_data['line_id'] = values['line_id']
                    joker_win_data['card_id'] = card.id
                    gross_weight += joker_win_data['weight'] - joker_win_data['tare']
                    joker_win = self.env['mdc.data_win'].create(joker_win_data)
                    ids_win.append(joker_win.id)
                else:
                    # TODO other card types (e.g. employee card....)
                    raise UserError(_("Unknown card #%s") % card.name)

        if not workstation_card:
            raise UserError(_("You must provide a workstation card"))

        wout_shared_data = None
        if values.get('shared', False):
            # Shared management
            # * Shared closing: there is a unlinked WOUT shared too with the same lot, line and seat
            wout_shared_data = self.search([('shared', '=', True), ('wout_shared_id', '=', False),
                                            ('lot_id', '=', values['lot_id']), ('line_id', '=', values['line_id']),
                                            ('workstation_id.seat', '=', workstation_card.workstation_id.seat)])
            if wout_shared_data:
                # TODO discard shared wout if it's the same worksheet (seat)?
                #      Temporally we prefer mantaining the shared self-closing option
                values['wout_shared_id'] = wout_shared_data.id
            else:
                # * Shared opening: others
                if len(card_ids) < 2:
                    raise UserError(_("It's not allowed to open a shared output without registering any product input"))



        values['gross_weight'] = gross_weight
        sp1_wout_categ = self.env.ref('mdc.mdc_wout_categ_SP1')
        # TODO Lot should be filled from view for testing purposes. Actually, it should always be computed
        if current_lot_id:
            values['lot_id'] = current_lot_id.id
        elif values['wout_categ_id'] == sp1_wout_categ.id:
            # If scrumbs output mode is selected, lot is calculated at this time as the last used by this workstation
            if workstation_card.workstation_id.last_wout_lot_id:
                values['lot_id'] = workstation_card.workstation_id.last_wout_lot_id.id
            else:
                if not values['lot_id']:  # values['lot_id'] bring chkpoint.current_lot_active_id
                    raise UserError(
                        _("Workstation %s has not any output nor there is current lot in checkpoint, so it's not yet allowed to make a %s output") %
                        (workstation_card.workstation_id.name, sp1_wout_categ.name))

        data_wout = super(DataWOut, self).create(values)

        # Close data_win entries
        if len(ids_win) > 0:
            data_win = self.env['mdc.data_win'].browse(ids_win)
            if data_win:
                for win in data_win:
                    win.write({
                        'wout_id': data_wout.id
                    })

        # If comes from a previous shared output, link themselves
        if wout_shared_data:
            wout_shared_data.write({
                'wout_shared_id': data_wout.id})

        # Finaly calculate total gross weight in lot
        # self.env['mdc.lot'].compute_total_gross_weight({'lot_id': values['lot_id']})

        return data_wout

    def from_cp_create(self, values):
        '''
        Saves a checkpoint entry from some input data
        '''

        # Data received:
        # - checkpoint_id
        # - cards_in
        # - card_workstation
        # - quality_id
        # - wout_categ_code
        wout_categ_id = self.env['mdc.wout_categ'].search([('code', '=', values['wout_categ_code'])])
        if not wout_categ_id:
            raise UserError(_('WOUT categ code #%s not found') % values['wout_categ_code'])
        chkpoint = self.env['mdc.chkpoint'].browse(values['chkpoint_id'])
        if not chkpoint:
            raise UserError(_('Checkpoint #%s not found') % values['chkpoint_id'])
        if not chkpoint.scale_id:
            raise UserError(_("Scale not defined"))
        if not chkpoint.tare_id:
            raise UserError(_("Tare not defined"))
        try:
            weight_value, weight_uom_id, weight_stability = chkpoint.scale_id.get_weight()[0:3]
        except socket.timeout:
            raise UserError(_("Timed out on weighing scale"))

        if weight_stability == 'unstable':
            raise UserError(_('Unstable %.2f %s weight was read. Please start passing cards again') %
                            (weight_value, weight_uom_id.name))

        cards_id_list = [] if len(values['cards_in']) == 0 else [card['card_id'] for card in values['cards_in']]
        cards_id_list.append(values['card_workstation']['card_id'])
        card_ids = [(6, False, cards_id_list)]

        # TODO if there is no input associated (e.g. shared mode without inputs) we should omit the lot and calculate it
        lot_id = chkpoint.current_lot_active_id.id if len(values['cards_in']) == 0 \
            else values['cards_in'][0]['win_lot_id']

        return self.create({
            'line_id': chkpoint.line_id.id,
            'lot_id': lot_id,
            'tare': chkpoint.tare_id.tare,
            'weight': weight_value,
            'w_uom_id': weight_uom_id.id,
            'quality_id': values['quality_id'],
            'shared': values['shared'],
            'wout_categ_id': wout_categ_id.id,
            'card_ids': card_ids
        })


