# -*- coding: utf-8 -*-

import logging
import datetime
from odoo import api, models, fields, _, registry
from odoo.exceptions import UserError, AccessError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DF

from .. import ws_rfid_server
import websocket
import ast


_logger = logging.getLogger(__name__)


class Lot(models.Model):
    """
    Main data for Lot (Manufacturing Orders Lots)
    """
    _name = 'mdc.lot'
    _description = 'Lot'

    _sql_constraints = [
        ('lot_name_unique', 'UNIQUE(name)',
         _('The selected lot name already exists')),
    ]

    def _default_date(self):
        #return fields.Datetime.from_string(fields.Datetime.now())
        return fields.Datetime.now()
    def _default_uom(self):
        return self.env.ref('product.product_uom_kgm')

    name = fields.Char(
        'MO',
        required=True)
    product_id = fields.Many2one(
        'product.product',
        string='Product (Standard)',
        required=True)
    weight =fields.Float(
        'Weight',
        required=True)
    w_uom_id = fields.Many2one(
        'product.uom',
        string = 'Weight Unit',
        default=_default_uom)
    partner_id = fields.Many2one(
        'res.partner',
        string='Customer')
    lot_code= fields.Char(
        'Lot',
        required=True)
    descrip = fields.Text(
        'Observations')
    start_date = fields.Date(
        'Start Date',
        required=True,
        default=_default_date)
    end_date = fields.Date(
        'End_Date',
        required=True)
    std_id = fields.Many2one(
        'mdc.std',
        string='Id Standard',
        ondelete='restrict')
    std_loss = fields.Float(
        'Std Loss')
    std_yield_product = fields.Float(
        'Std Yield Product',
        digits=(10,3))
    std_speed = fields.Float(
        'Std Speed',
        digits=(10,3))
    std_yield_sp1 = fields.Float(
        'Std Yield Subproduct 1',
        digits=(10,3))
    std_yield_sp2 = fields.Float(
        'Std Yield Subproduct 2',
        digits=(10,3))
    std_yield_sp3 = fields.Float(
        'Std Yield Subproduct 3',
        digits=(10,3))
    total_gross_weight = fields.Float(
        'Real Total Gross Weight',
        # compute='_compute_total_gross_weight',
        readonly=True,
        # store=True,
        default=0)
    alias_cp = fields.Char(
        'Alias CP name',
        compute='_compute_alias_cp',
    )
    wout_ids = fields.One2many(
        'mdc.data_wout',
        'lot_id')
    finished = fields.Boolean(
        'Lot finished',
        default=False)

    def name_get(self, context=None):
        if context is None:
            context = {}
        res = []
        # FIXME it Doesn't Work - it always goes inside the if lines
        if context.get('name_extended', True):
            # Only one context possible
            for entry in self:
                if not entry.partner_id.name:
                    cliente = ''
                else:
                    cliente = entry.partner_id.name
                if not entry.end_date:
                    caduca = ''
                else:
                    caduca = entry.end_date
                prod_name= self.env['product.product'].browse(entry.product_id.id).name_get()[0][1]
                res.append((entry.id, '[%s (%s , %s)]: %s - (%s)' % (entry.name, entry.start_date, caduca, prod_name, cliente)))
        else:
            for entry in self:
                res.append((entry.id, '%s' % (entry.name)))
        return res

    def _lot_format(self, values):
        lotName = values['name']
        if lotName is None or lotName is False or lotName == '':
            return ''
        # lotPart2 must be current year (las 2 digits)
        currYear2 = str(datetime.datetime.now().year)[2:4]
        lotPart1 = '1'
        lotPart2 = currYear2
        lotRightFormat = True
        if lotName.find('/') > 0:
            lotPart1 = lotName[0:lotName.find('/')]
            lotPart2 = lotName[lotName.find('/')+1:len(lotName)]
        if lotName.find('/') == -1:
            lotPart1 = lotName
        if not lotPart1.isnumeric() or len(lotPart1) > 5:
            raise UserError(_('MO Format is not right. The right format is NNNNN/AA (NNNNN=number)'))
        if lotPart2 != currYear2:
            raise UserError(_('MO Format is not right. The right format is NNNNN/AA (AA=current year) %s != %s')
                              % (lotPart2, currYear2))

        return lotPart1.zfill(5)+'/'+lotPart2

    # compute total_gross_
    """
    def compute_total_gross_weight(self, context):
        tot_gross_weight = 0
        woutlot = self.env['mdc.data_wout'].search([('lot_id', '=', context['lot_id'])])
        for wo in woutlot:
            tot_gross_weight += wo.gross_weight
        lot = self.browse(context['lot_id'])
        if lot:
            lot.total_gross_weight = tot_gross_weight
    """

    """
    # @api.depends('wout_ids')
    def _compute_total_gross_weight(self):
        for lot in self:
            lot.total_gross_weight = sum(lot.wout_ids.mapped('gross_weight'))
    """

    @api.model
    def _update_total_gross_weight(self):
        try:
            current_timestamp = int(fields.datetime.now().timestamp())
            _logger.debug('[_update_total_gross_weight] Next update timestamp: %s' % current_timestamp)
            IrConfigParameter = self.env['ir.config_parameter']
            last_timestamp = int(IrConfigParameter.get_param('mdc.lot_last_total_gross_weight_update_timestamp'))
            _logger.debug('[_update_total_gross_weight] Former update timestamp: %s' % last_timestamp)
            last_datetime = fields.Datetime.to_string(datetime.datetime.fromtimestamp(last_timestamp))
            lot_ids = self.env['mdc.data_wout'].search([('write_date', '>=', last_datetime)]).mapped('lot_id')
            for lot in lot_ids:
                lot.total_gross_weight = sum(lot.wout_ids.mapped('gross_weight'))
            IrConfigParameter.set_param('mdc.lot_last_total_gross_weight_update_timestamp', current_timestamp)
            _logger.info('[_update_total_gross_weight] Process finished for %d lots. New timestamp: %s' %
                         (len(lot_ids), current_timestamp))
        except Exception as e:
            _logger.error('[_update_total_gross_weight] %s' % e)

    @api.multi
    @api.depends('name', 'lot_code')
    def _compute_alias_cp(self):
        for lot in self:
            lot.alias_cp = '%s - %s' % (lot.name, lot.lot_code or '')

    @api.constrains('end_date')
    def _check_end_date(self):
        for l in self:
            if l.end_date < l.start_date:
                raise models.ValidationError(_('End date must be older than start date'))

    @api.onchange('name')
    def _retrieve_lot_format(self):
        for lot in self:
            lot.name = self._lot_format({'name': lot.name})

    @api.onchange('product_id')
    def _retrieve_std_data(self):
        for lot in self:
            std = self.env['mdc.std'].search([('product_id', '=', lot.product_id.id)])
            lot.std_id = std.id
            lot.std_loss = std.std_loss
            lot.std_yield_product = std.std_yield_product
            lot.std_speed = std.std_speed
            lot.std_yield_sp1 = std.std_yield_sp1
            lot.std_yield_sp2 = std.std_yield_sp2
            lot.std_yield_sp3 = std.std_yield_sp3

    @api.onchange('start_date')
    def _calculate_end_date(self):
        IrConfigParameter = self.env['ir.config_parameter'].sudo()
        default_life_days = int(IrConfigParameter.get_param('mdc.lot_default_life_days'))
        for lot in self:
            if lot.start_date is not None:
                w_start_date = fields.Datetime.from_string(lot.start_date)
                w_end_date = w_start_date + datetime.timedelta(days=default_life_days)
                lot.end_date = w_end_date.strftime("%Y-%m-%d %H:%M:%S")
            else:
                lot.end_date = None


class LotActive(models.Model):
    """
    Main data for active lots
    """
    _name = 'mdc.lot_active'
    #_inherit = ['mdc.base.structure']
    _description = 'Active Lot'

    def _get_chkpoint_categ_selection(self):
        return [
            ('WIN', _('Input')),
            ('WOUT', _('Output')),
    ]

    def _default_date(self):
        #return fields.Datetime.from_string(fields.Datetime.now())
        return fields.Datetime.now()

    lot_id = fields.Many2one(
        'mdc.lot',
        string='MO',
        required=True)
    chkpoint_id = fields.Many2one(
        'mdc.chkpoint',
        string='Checkpoint Id',
        required=True)
    shift_id = fields.Many2one(
        'mdc.shift',
        string='shift Id')
    start_datetime = fields.Datetime(
        'Datetime_Start',
        required=True,
        default=_default_date)
    end_datetime = fields.Datetime(
        'Datetime_End')
    total_hours = fields.Float(
        'Total hours',
        readonly=True,
        default=0)
    active = fields.Boolean(
        'Active',
        default=True)

    def _compute_total_hours(self, values):
        total_hours = 0.0
        start_datetime = self.start_datetime
        if 'start_datetime' in values:
            start_datetime = values['start_datetime']
        end_datetime = self.end_datetime
        if 'end_datetime' in values:
            end_datetime = values['end_datetime']
        if end_datetime is False:
            end_datetime = fields.Datetime.now()
        if start_datetime is not False and end_datetime is not False and start_datetime < end_datetime:
            difference = fields.Datetime.from_string(end_datetime) - fields.Datetime.from_string(start_datetime)
            total_hours = difference.total_seconds() / 3600
        return total_hours

    @api.constrains('start_datetime')
    def _check_start_datetime(self):
        for l in self:
            if not l.start_datetime and l.start_datetime > fields.Datetime.now():
                raise UserError(_('You can´t give a future start date'))
            id_lot_active = self.search(
                [('chkpoint_id', '=', l.chkpoint_id.id),
                 ('shift_id', '=', l.shift_id.id),
                 ('end_datetime', '>', l.start_datetime)])
            if id_lot_active:
                raise models.ValidationError(_('Start date must be older last end date'))

    @api.constrains('end_datetime')
    def _check_end_datetime(self):
        for l in self:
            if not l.end_datetime and l.end_datetime > fields.Datetime.now():
                raise UserError(_('You can´t give a future end date'))
            if l.end_datetime < l.start_datetime:
                raise models.ValidationError(_('End date must be older than start date'))

    @api.model
    def create(self, values):
        values['total_hours'] = self._compute_total_hours(values)
        return super(LotActive, self).create(values)

    @api.multi
    def write(self, values):
        self.ensure_one()

        if ('lot_id' in values) or ('chkpoint_id' in values) or ('shift_id' in values):
            raise AccessError(_("Neither the lot nor the checkpoint not the sift can be modified"))

        if 'start_datetime' in values:
            _logger.info("[mdc.lot_active - write]: values['start_datetime'] %s, self.start_datetime: %s"
                         % (values['start_datetime'], self.start_datetime))

        # update (if exists) historic lot with end_datetime the old start_date time
        if 'start_datetime' in values and values['start_datetime'] and self.start_datetime \
                and values['start_datetime'] != self.start_datetime:
            # update (if exists) historic lot with end_datetime the old start_date time
            _logger.info("[mdc.lot_active - write]: -> search change start_datetime: chkpoint_id: %s, shift_id: %s, end_datetime: %s"
                            % (self.chkpoint_id.id, self.shift_id.id, self.start_datetime))
            id_lot_search = self.search([('chkpoint_id', '=', self.chkpoint_id.id), ('shift_id', '=', self.shift_id.id),
                                         ('end_datetime', '=', self.start_datetime)])
            if not id_lot_search:
                # if we don´t find it at first, we search with active = False
                id_lot_search = self.search([('chkpoint_id', '=', self.chkpoint_id.id), ('shift_id', '=', self.shift_id.id),
                                             ('end_datetime', '=', self.start_datetime), ('active', '=', False)])
            if id_lot_search:
                _logger.info("[mdc.lot_active - write]: id_lot: %s, update end_datetime: from %s to %s"
                            % (id_lot_search.id, id_lot_search.end_datetime, values['start_datetime']))
                id_lot_search.write({
                    'end_datetime': values['start_datetime'],
                    'total_hours': -1
                })
            else:
                _logger.info("[mdc.lot_active - write]: -> search change start_datetime: don´t find")

            # calculate de interval of change
            start_change_interval = values['start_datetime']
            end_change_interval = self.start_datetime
            lot_active_interval = self.lot_id.id
            if 'lot_id' in values and not values['lot_id']:
                lot_active_interval = values['lot_id'].id
            if self.start_datetime < values['start_datetime']:
                start_change_interval = self.start_datetime
                end_change_interval = values['start_datetime']
                if id_lot_search:
                    lot_active_interval = id_lot_search.lot_id.id
                else:
                    lot_active_interval = 0

            # if a checkpoint WIN we have to validate that can´t have reg in data_win
            if self.chkpoint_id.chkpoint_categ == 'WIN':
                numReg = self.env['mdc.data_win'].count_nreg(
                    line_id=self.chkpoint_id.line_id,
                    start_change_interval=start_change_interval,
                    end_change_interval=end_change_interval)
                if numReg > 0:
                    raise UserError(_('You can´t change start date because there are %s reg. in the interval of change')% str(numReg))

            # if a checkpoint WOUT we have to refactoring the worksheet in this interval
            if self.chkpoint_id.chkpoint_categ == 'WOUT':
                Worksheet = self.env['mdc.worksheet']
                if not Worksheet.check_permissions():
                    raise UserError(_("You don't have permissions to this operation"))
                Worksheet.sudo().refactoring(
                    line_id=self.chkpoint_id.line_id,
                    shift_id=self.shift_id,
                    lot_active_interval=lot_active_interval,
                    start_change_interval=start_change_interval,
                    end_change_interval=end_change_interval)

        if 'end_datetime' in values:
            _logger.info("[mdc.lot_active - write]: values['end_datetime'] %s, self.end_datetime: %s"
                         % (values['end_datetime'], self.end_datetime))

        # update (if exists) historic lot with start_datetime the old end_date time
        if 'end_datetime' in values and values['end_datetime'] and self.end_datetime \
                and values['end_datetime'] != self.end_datetime:
            fromModifStartDate = False
            #we know we went from update start_date because 'total_hours': -1
            if 'total_hours' in values and values['total_hours'] == -1:
                fromModifStartDate = True
            if not fromModifStartDate:
                _logger.info("[mdc.lot_active - write]: -> search change end_datetime: chkpoint_id: %s, shift_id: %s, start_datetime: %s"
                             % (self.chkpoint_id.id, self.shift_id.id, self.end_datetime))
                id_lot_search = self.search([('chkpoint_id', '=', self.chkpoint_id.id), ('shift_id', '=', self.shift_id.id),
                                             ('start_datetime', '=', self.end_datetime)])
                if not id_lot_search:
                    # if we don´t find it at first, we search with active = False
                    id_lot_search = self.search([('chkpoint_id', '=', self.chkpoint_id.id), ('shift_id', '=', self.shift_id.id),
                                                 ('start_datetime', '=', self.end_datetime), ('active', '=', False)])
                if id_lot_search:
                    raise UserError(_( 'You can´t change this end datetime. You must change the start date of the active lot with start date this end date'))
                else:
                    _logger.info("[mdc.lot_active - write]: -> search change end_datetime: don´t find")
                # calculate de interval of change
                start_change_interval = values['end_datetime']
                end_change_interval = self.end_datetime
                if id_lot_search:
                    lot_active_interval = id_lot_search.lot_id.id
                else:
                    lot_active_interval = 0
                if self.end_datetime < values['end_datetime']:
                    start_change_interval = self.end_datetime
                    end_change_interval = values['end_datetime']
                    lot_active_interval = self.lot_id.id
                    if 'lot_id' in values and not values['lot_id']:
                        lot_active_interval = values['lot_id'].id

                # if a checkpoint WIN we have to validate that can´t have reg in data_win
                if self.chkpoint_id.chkpoint_categ == 'WIN':
                    numReg = self.env['mdc.data_win'].count_nreg(
                        line_id=self.chkpoint_id.line_id,
                        start_change_interval=start_change_interval,
                        end_change_interval=end_change_interval)
                    if numReg > 0:
                        raise UserError(_('You can´t change end date because there are %s reg. in the interval of change') % str(numReg))

                # if a checkpoint WOUT we have to refactoring the worksheet in this interval
                if self.chkpoint_id.chkpoint_categ == 'WOUT':
                    Worksheet = self.env['mdc.worksheet']
                    if not Worksheet.check_permissions():
                        raise UserError(_("You don't have permissions to this operation"))
                    Worksheet.sudo().refactoring(
                        line_id=self.chkpoint_id.line_id,
                        shift_id=self.shift_id,
                        lot_active_interval=lot_active_interval,
                        start_change_interval=start_change_interval,
                        end_change_interval=end_change_interval)

        # compute total hours
        values['total_hours'] = self._compute_total_hours(values)
        return super(LotActive, self).write(values)


    def update_historical(self, chkpoint_id, line_id, shift_id, current_lot_active, new_lot_active_id, start_lot_datetime):
        # first validate if there are data_win after start_lot_datetime change
        chkpoint_data = self.env['mdc.chkpoint'].browse(chkpoint_id)
        if chkpoint_data.chkpoint_categ == "WIN":
            numReg = self.env['mdc.data_win'].count_nreg(
                line_id=chkpoint_data.line_id,
                start_change_interval=start_lot_datetime,
                end_change_interval=fields.Datetime.now())
            if numReg > 0:
                raise UserError(_('You can´t put this date because there are %s reg. in after this') % str(numReg))

        # Modifying a current_lot_active
        if (current_lot_active) and (current_lot_active.id != new_lot_active_id):
            # In this case, Close historic lot_active
            id_lot_active = self.search([('lot_id', '=', current_lot_active.id), ('chkpoint_id', '=', chkpoint_id),
                                         ('shift_id', '=', shift_id.id), ('end_datetime', '=', False)])
            if id_lot_active:
                _logger.info("[mdc.lot_active - update_historical]: lot_id: %s, chkpoint_id: %s, shift_id: %s, update end_datetime from False to %s."
                            % (current_lot_active.id, chkpoint_id, shift_id.id, start_lot_datetime))
                id_lot_active.write({
                    'end_datetime': start_lot_datetime,
                    'active': False,
                })
        if (new_lot_active_id) and (current_lot_active.id != new_lot_active_id):
            _logger.info("[mdc.lot_active - update_historical]: create reg lot_id: %s, chkpoint_id: %s, shift_id: %s, start_datetime: %s"
                         % (new_lot_active_id, chkpoint_id, shift_id.id, start_lot_datetime))
            # In this case, Open new historic lot_active
            self.create({
                'lot_id': new_lot_active_id,
                'chkpoint_id': chkpoint_id,
                'shift_id': shift_id.id,
                'start_datetime': start_lot_datetime
            })

        # Only when lot_active has changed and chkpoint type is WOUT,
        #  we must close the related worksheets and open new ones
        if chkpoint_data.chkpoint_categ == 'WOUT':
            Worksheet = self.env['mdc.worksheet']
            if not Worksheet.check_permissions():
                raise UserError(_("You don't have permissions to this operation"))
            Worksheet.sudo().new_lot_active(
                line_id=line_id,
                shift_id=shift_id,
                new_lot_active_id=new_lot_active_id,
                start_lot_datetime=start_lot_datetime)
        return

    def update_start_date(self, chkpoint_id, shift_id, new_lot_active_id, new_start_lot_datetime, old_start_lot_datetime):
        _logger.info("[mdc.lot_active - update_start_date]: chkpoint_id: %s, shift_id: %s, new_lot_active_id: %s, new_start_lot_datetime: %s, old_start_lot_datetime: %s"
                    % (chkpoint_id, new_lot_active_id, shift_id.id, new_start_lot_datetime, old_start_lot_datetime))
        # update (if exists) historic lot with start_datetime the old start_date time
        id_lot_search = self.search( [('chkpoint_id', '=', chkpoint_id), ('shift_id', '=', shift_id.id),
                                      ('start_datetime', '=', old_start_lot_datetime)])
        if id_lot_search:
            _logger.info("[mdc.lot_active - update_start_date]: find: id_lot: %s, change start_datetime from %s to %s."
                        % (id_lot_search.id, id_lot_search.start_datetime, new_start_lot_datetime))
            id_lot_search.write({
                'start_datetime': new_start_lot_datetime
            })
        else:
            if not new_lot_active_id or new_lot_active_id == 0:
                id_lot_search = self.search([('chkpoint_id', '=', chkpoint_id), ('shift_id', '=', shift_id.id),
                                             ('end_datetime', '=', old_start_lot_datetime), ('active', '=', False)])
                if id_lot_search:
                    _logger.info("[mdc.lot_active - update_start_date]: find update_end_date: %s new_end_lot_datetime: %s"
                                % (id_lot_search.id, new_start_lot_datetime))
                    id_lot_search.write({
                        'end_datetime': new_start_lot_datetime
                    })

        return

    def _online_update_total_hours(self):
        """
        Calculate total hours of lots without end date
        :return:
        """
        opened_lotActive = self.search([('end_datetime', '=', False)])
        if opened_lotActive:
            try:
                for lot in opened_lotActive:
                    # we execute write method without calculate total hours (we send zero)
                    # because in write method we calculate the real total_hours
                    lot.write({'total_hours': 0})
                    _logger.debug('[mdc.lot_active] update_total_hours %s' % (lot.lot_id.name))
            except UserError as e:
                _logger.error('[mdc.lot_active] _online_update_total_hours:  %s' % e)
            _logger.info('[_online_update_total_hours] Process finished for %d opened lots' % len(opened_lotActive))
        """
        Calculate total hours of worksheet without end date
        :return:
        """
        opened_worksheet = self.env['mdc.worksheet'].search([('end_datetime', '=', False)])
        if opened_worksheet:
            try:
                for ws in opened_worksheet:
                    # we execute write method without calculate total hours (we send zero)
                    # because in write method we calculate the real total_hours
                    ws.write({'total_hours': 0})
                    _logger.debug('[mdc.worksheet] update_total_hours %s - %s' % (ws.employee_id.name, ws.workstation_id.name))
            except UserError as e:
                _logger.error('[mdc.worksheet] _online_update_total_hours:  %s' % e)
            _logger.info('[_online_update_total_hours] Process finished for %d opened worksheets' % len(opened_worksheet))

class Worksheet(models.Model):
    """
    Detailled employee time
    """
    _name = 'mdc.worksheet'
    _description = 'Worksheet'

    def _default_date(self):
        #return fields.Datetime.from_string(fields.Datetime.now())
        return fields.Datetime.now()

    employee_id = fields.Many2one(
        'hr.employee',
        string='Employee',
        required = True)
    start_datetime = fields.Datetime(
        'Start Datetime',
        required=True,
        default = _default_date)
    end_datetime = fields.Datetime(
        'End Datetime')
    manual_open = fields.Boolean(
        default=False)
    manual_close = fields.Boolean(
        default=False)
    physical_open = fields.Boolean(
        'Physical open',
        default=False)
    physical_close = fields.Boolean(
        'Physical close',
        default=False)
    physical_start_datetime = fields.Datetime(
        'Real Start Datetime')
    physical_end_datetime = fields.Datetime(
        'Real End Datetime')
    lot_id = fields.Many2one(
        'mdc.lot',
        string='MO',
        readonly=True)
    workstation_id = fields.Many2one(
        'mdc.workstation',
        string='Workstation',
        readonly=True)
    shift_id = fields.Many2one(
        'mdc.shift',
        string='Shift',
        readonly=True)
    total_hours = fields.Float(
        'Total hours',
        readonly=True,
        default=0)

    def _retrieve_shift(self, values):
        shift = False
        workstation_id = self.workstation_id
        if 'workstation_id' in values:
            workstation_id = values['workstation_id']
        if workstation_id is not False:
            workstation = self.env['mdc.workstation'].browse(workstation_id.id)
            if workstation:
                shift = workstation.shift_id.id
        return shift

    @api.constrains('end_datetime')
    def _check_end_datetime(self):
        for l in self:
            if l.end_datetime is not False and l.start_datetime is not False \
                    and l.end_datetime < l.start_datetime:
                raise models.ValidationError(_('End date must be older than start date'))

    @api.onchange('workstation_id')
    def _retrieve_workstation_data(self):

        for worksheet in self:
            # search shift of workstation
            if worksheet.workstation_id:
                worksheet.shift_id = worksheet.workstation_id.shift_id

    def _compute_total_hours(self, values):
        total_hours = 0
        start_datetime = self.start_datetime
        if 'start_datetime' in values:
            start_datetime = values['start_datetime']
        end_datetime = self.end_datetime
        if 'end_datetime' in values:
            end_datetime = values['end_datetime']
        if end_datetime is False:
            end_datetime = fields.Datetime.now()
        if start_datetime is not False and end_datetime is not False and start_datetime < end_datetime:
            end_date = fields.Datetime.from_string(end_datetime)
            start_date = fields.Datetime.from_string(start_datetime)
            timedelta = end_date - start_date
            total_hours = timedelta.total_seconds() / 3600

        return total_hours

    @api.onchange('start_datetime', 'end_datetime')
    def _retrieve_total_hours(self):

        for worksheet in self:
            # compute total_hours
            values = {'start_datetime': worksheet.start_datetime,
                      'end_datetime': worksheet.end_datetime }
            worksheet.total_hours = worksheet._compute_total_hours(values)

    @api.model
    def create(self, values):
        line_id = False
        shift_id = False
        em = self.env['hr.employee'].browse(values['employee_id'])
        if 'start_datetime' in values:
            # start_datetime must to be greater than last end_datetime
            if em.worksheet_end_datetime is not False and 'end_datetime' not in values \
                and str(values['start_datetime']) < str(em.worksheet_end_datetime):
                _logger.error("[mdc.worksheet - create] employee_id: %s , values['start_datetime'] < em.worksheet_end_datetime: %s"
                        % (em.id, values['start_datetime'], em.worksheet_end_datetime))
                raise UserError(_('It can´t be start datetime less than last end datetime to employee %s') % em.employee_code)
        else:
            # must be give a start date
            raise UserError(_('The start date has to be filled'))
        if 'end_datetime' in values:
            # end_datetime must to be greater than start_datetime
            if values['end_datetime'] is not False and str(values['end_datetime']) < str(values['start_datetime']):
                raise UserError(_('It can´t be end datetime less than start date to employee %s') % em.employee_code)
        if 'workstation_id' not in values:
            # get workstation pre-assigned data from employee (if the employee was pre-assigned to a workstation)
            (ws_id, shift_id, line_id) = self.env['mdc.workstation'].get_workstation_data_by_employee(values['employee_id'])
            values['workstation_id'] = ws_id
            values['shift_id'] = shift_id
        else:
            # get shift and line for specific workstation
            if values['workstation_id']:
                ws = self.env['mdc.workstation'].browse(values['workstation_id'])
                line_id = ws.line_id.id
                shift_id = ws.shift_id.id
                values['shift_id'] = shift_id
        # with line, get lot from chkpoint (WOUT chkpoint)
        if 'lot_id' not in values:
            if line_id:
                ws_start_datetime = values['start_datetime']
                ws_end_datetime = False
                if 'end_datetime' in values:
                    ws_end_datetime = values['end_datetime']
                checkpoint = self.env['mdc.chkpoint'].search([('chkpoint_categ', '=', 'WOUT'),
                                                              ('line_id', '=', line_id)])
                lotchckpoint = self.env['mdc.lot_chkpoint'].search([('chkpoint_id', '=', checkpoint.id),
                                                                    ('shift_id', '=', shift_id)])
                if lotchckpoint and lotchckpoint.start_lot_datetime \
                and lotchckpoint.start_lot_datetime > values['start_datetime']:
                    ws_last_end_datetime = values['start_datetime']
                    lot = self.env['mdc.lot_active'].search([('chkpoint_id', '=', checkpoint.id),
                                                             ('shift_id', '=', shift_id),
                                                             ('start_datetime', '<', lotchckpoint.start_lot_datetime),
                                                             ('end_datetime', '>=', values['start_datetime']),
                                                             ('active', '=', False)],
                                                        order='start_datetime asc')
                    if lot:
                        for lt in lot:
                            #create the last historic lots
                            if lt.start_datetime > ws_last_end_datetime:
                                # create worksheet without lot
                                values['start_datetime'] = ws_last_end_datetime
                                if ws_end_datetime and ws_end_datetime <= lt.start_datetime:
                                    values['end_datetime'] = ws_end_datetime
                                else:
                                    values['end_datetime'] = lt.start_datetime
                                values['lot_id'] = None
                                values['total_hours'] = self._compute_total_hours(values)
                                wsheet = super(Worksheet, self).create(values)
                                if ws_end_datetime and ws_end_datetime <= lt.start_datetime:
                                    return wsheet
                                ws_last_end_datetime = lt.start_datetime
                            # create worksheet without the historic lot
                            values['start_datetime'] = ws_last_end_datetime
                            if ws_end_datetime and ws_end_datetime <= lt.end_datetime:
                                values['end_datetime'] = ws_end_datetime
                            else:
                                values['end_datetime'] = lt.end_datetime
                            values['lot_id'] = lt.lot_id.id
                            values['total_hours'] = self._compute_total_hours(values)
                            wsheet = super(Worksheet, self).create(values)
                            if ws_end_datetime and ws_end_datetime <= lt.end_datetime:
                                return wsheet
                            ws_last_end_datetime = lt.end_datetime

                    if ws_last_end_datetime < lotchckpoint.start_lot_datetime:
                        # create worksheet without lot
                        values['start_datetime'] = ws_last_end_datetime
                        if ws_end_datetime and ws_end_datetime <= lotchckpoint.start_lot_datetime:
                            values['end_datetime'] = ws_end_datetime
                        else:
                            values['end_datetime'] = lotchckpoint.start_lot_datetime
                        values['lot_id'] = None
                        values['total_hours'] = self._compute_total_hours(values)
                        wsheet = super(Worksheet, self).create(values)
                        if ws_end_datetime and ws_end_datetime <= lotchckpoint.start_lot_datetime:
                            return wsheet
                    # put start_datetime whith then start_lot_datetime
                    values['start_datetime'] = lotchckpoint.start_lot_datetime
                    values['end_datetime'] = ws_end_datetime
                if ws_end_datetime is False or lotchckpoint.start_lot_datetime < ws_end_datetime:
                    values['lot_id'] = lotchckpoint.current_lot_active_id.id
                else:
                    values['lot_id'] = None
        values['total_hours'] = self._compute_total_hours(values)
        return super(Worksheet, self).create(values)

    @api.multi
    def write(self, values):
        self.ensure_one()
        if 'employee_id' in values:
            if self.employee_id.id != values['employee_id']:
                raise UserError(_('You can´t change employee form a datasheet.'))
        w_start_datetime = False
        w_end_datetime = False
        if 'start_datetime' in values:
            w_start_datetime = values['start_datetime']
        else:
            if self.start_datetime:
                w_start_datetime = self.start_datetime

        if 'end_datetime' in values:
            w_end_datetime = values['end_datetime']
        else:
            if self.end_datetime:
                w_end_datetime = self.end_datetime
            else:
                if self.employee_id.worksheet_end_datetime:
                    # start_datetime must to be greater than last end_datetime
                    if 'start_datetime' in values and str(w_start_datetime) < str(self.employee_id.worksheet_end_datetime):
                        _logger.error("[mdc.worksheet - write] employee_id: %s , w_start_datetime: %s < w_end_datetime: %s"
                                      % (self.employee_id.id, w_start_datetime, self.employee_id.worksheet_end_datetime))
                        raise UserError(_('It can´t be start datetime less than last end datetime to employee %s') % self.employee_id.employee_code)

        # end_datetime must to be greater than start_datetime
        if w_start_datetime and w_end_datetime and str(w_end_datetime) < str(w_start_datetime):
            raise UserError(
                _('It can´t be end datetime less than start date to employee %s') % self.employee_id.employee_code)

        values['total_hours'] = self._compute_total_hours(values)
        return super(Worksheet, self).write(values)

    @api.constrains('manual_open', 'manual_close', 'physical_open',
                    'physical_close', 'end_datetime')
    def _check_flags(self):
        for worksheet in self:
            if worksheet.manual_open and worksheet.physical_open:
                raise UserError(_(
                    'Cannot set manual open to a worksheet '
                    'with physical open for employee %s') %
                                worksheet.employee_id.employee_code)
            if worksheet.manual_close:
                if worksheet.physical_close:
                    raise UserError(_(
                        'Cannot set manual close to a worksheet '
                        'with physical close for employee %s') %
                                    worksheet.employee_id.employee_code)
                if not worksheet.end_datetime:
                    raise UserError(_(
                        'Cannot set manual close to a worksheet '
                        'without End datetime for employee %s') %
                                    worksheet.employee_id.employee_code)

    @api.multi
    def massive_close(self, wsheets, end_time):
        for item in wsheets:
            item.write({'end_datetime': end_time})
        return

    @api.multi
    def update_employee_worksheets(self, employee_id, new_workstation_id, now):
        # Look for employee open worksheets, and close them
        if not self.user_has_groups('mdc.group_mdc_office_worker'):
            raise UserError(_('You are not allowed to change this values'))
        wsheet = self.sudo().search(
            [('end_datetime', '=', False),
             ('employee_id', '=', employee_id)])
        self.sudo().massive_close(wsheet, now)
        # with new workstation create a new worksheet for this employee
        self.sudo().create({
            'start_datetime': now,
            'employee_id': employee_id,
            'workstation_id': new_workstation_id})
        return

    def check_permissions(self):
        return self.env.user.has_group('mdc.group_mdc_office_worker')

    def new_lot_active(self, line_id, shift_id, new_lot_active_id, start_lot_datetime):
        _logger.info("[mdc.worksheet - new_lot_active]: line_id: %s, shift_id: %s, current_lot_active_id: %s, start_lot_datetime: %s"
                     % (line_id.id, shift_id.id, new_lot_active_id, start_lot_datetime))
        # if start_lot_datetime < now we have to control if there are worksheet opened or closed between start_lot_datetime and now
        start_change_interval = start_lot_datetime
        end_change_interval = start_lot_datetime
        now = fields.Datetime.now()
        if start_lot_datetime < now:
            numReg = self.search_count(
                ['|', '&', '&', '&', ('workstation_id.line_id', '=', line_id.id), ('shift_id', '=', shift_id.id),
                 ('end_datetime', '>=', start_lot_datetime), ('end_datetime', '<=', now),
                 '&', '&', '&', ('workstation_id.line_id', '=', line_id.id), ('shift_id', '=', shift_id.id),
                 ('start_datetime', '>=', start_lot_datetime), ('start_datetime', '<=', now)
                 ])
            if numReg > 0:
                # if there are worksheet we have to do the massive change first with date = now
                _logger.info("[mdc.worksheet - new_lot_active]: numReg: %s" % numReg)
                end_change_interval = now
        # step 1.- do massive and create worksheet with date start_lot_datetime or now
        ws = self.search(
            [('end_datetime', '=', False),
             ('workstation_id.line_id', '=', line_id.id),
             ('workstation_id.shift_id', '=', shift_id.id)])
        if ws:
            _logger.info("[mdc.worksheet - new_lot_active]: massive_close with date: %s" % end_change_interval)
            self.massive_close(ws, end_change_interval)
            for employee in ws.mapped('employee_id'):
                _logger.info("[mdc.worksheet - new_lot_active]: create: employee_id: %s, lot_id: %s, start_datetime: %s"
                             % (employee.id, new_lot_active_id, end_change_interval))
                self.create({
                    'start_datetime': end_change_interval,
                    'employee_id': employee.id,
                    'lot_id': new_lot_active_id})
        # step 2.- if there are worksheet opened or closed between start_lot_datetime and now
        #           we have to call to refactoring method with the interval start_lot_datetime and now
        if end_change_interval > start_change_interval:
            _logger.info("[mdc.worksheet - new_lot_active]: end_change_interval: %s > start_change_interval: %s"
                         % (end_change_interval, start_change_interval))
            self.refactoring(
                line_id=line_id,
                shift_id=shift_id,
                lot_active_interval=new_lot_active_id,
                start_change_interval=start_change_interval,
                end_change_interval=end_change_interval)

    def refactoring(self, line_id, shift_id, lot_active_interval, start_change_interval, end_change_interval):
        _logger.info("[mdc.worksheet - refactoring]: line_id: %s, shift_id: %s, lot_active_interval: %s, start_change_interval: %s, end_change_interval: %s"
                     % (line_id.id, shift_id.id, lot_active_interval, start_change_interval, end_change_interval))
        wsheet = self.search(
             ['|', '&', '&', '&', ('workstation_id.line_id', '=', line_id.id), ('shift_id', '=', shift_id.id),
                 ('end_datetime', '>=', start_change_interval), ('end_datetime', '<=', end_change_interval),
                 '&', '&', '&', ('workstation_id.line_id', '=', line_id.id), ('shift_id', '=', shift_id.id),
                 ('start_datetime', '>=', start_change_interval), ('start_datetime', '<=', end_change_interval)
             ], order='employee_id asc, start_datetime asc')
        numReg=0
        if wsheet:
            for ws in wsheet:
                numReg+=1
                _logger.info("[mdc.worksheet - refactoring]: %s find worksheet: ws.employee_id: %s, ws.lot_id : %s, ws.start_datetime: %s, ws.end_datetime:%s."
                             % (numReg, ws.employee_id.id, ws.lot_id.id, ws.start_datetime, ws.end_datetime))
                if ws.start_datetime < start_change_interval:
                    if ws.lot_id.id != lot_active_interval:
                        updateEndDate = True
                        if ws.end_datetime and ws.end_datetime == start_change_interval:
                            updateEndDate = False
                        if updateEndDate:
                            rs_old_end_datetime = ws.end_datetime  # set in a temp variable de rs.end_datetime before update then
                            _logger.info("[mdc.worksheet - refactoring]: - write worksheet: (id: %s) ws.employee_id: %s update end_datetime: from %s to %s."
                                         % (ws.id, ws.employee_id.id, ws.end_datetime, start_change_interval))
                            ws.write({'end_datetime': start_change_interval})
                            # if the next element has the same lot_id update the start_date of the next
                            ws2 = self.search([('employee_id', '=', ws.employee_id.id), ('start_datetime', '=', rs_old_end_datetime),
                                               ('workstation_id', '=', ws.workstation_id.id), ('shift_id', '=', ws.shift_id.id)])
                            updateStartDate = False
                            if ws2:
                                if not ws2.lot_id:
                                    if lot_active_interval == 0:
                                        updateStartDate = True
                                else:
                                    if lot_active_interval == ws2.lot_id.id:
                                        updateStartDate = True
                            if updateStartDate:
                                _logger.info("[mdc.worksheet - refactoring]: - write worksheet: (id: %s) ws.employee_id: %s update start_datetime: from %s to %s."
                                             % (ws2.id, ws.employee_id.id, ws2.start_datetime, start_change_interval))
                                ws2.write({'start_datetime': start_change_interval})
                            else:
                                _logger.info("[mdc.worksheet - refactoring]: - create worksheet: employee_id: %s, lot_id : %s, start_datetime: %s, end_datetime: %s."
                                             % (ws.employee_id.id, lot_active_interval, start_change_interval, rs_old_end_datetime))
                                self.create({
                                    'employee_id': ws.employee_id.id,
                                    'start_datetime': start_change_interval,
                                    'end_datetime': rs_old_end_datetime,
                                    'lot_id': lot_active_interval,
                                    'workstation_id': ws.workstation_id.id
                                })
                else:
                    if ws.lot_id.id != lot_active_interval:
                        if ws.end_datetime and ws.end_datetime <= end_change_interval:
                            # if the next element has the same lot_id update the start_date of the next
                            ws2 = self.search([('employee_id', '=', ws.employee_id.id), ('start_datetime', '=', ws.end_datetime),
                                               ('workstation_id', '=', ws.workstation_id.id), ('shift_id', '=', ws.shift_id.id)])
                            updateStartDate = False
                            if ws2:
                                if not ws2.lot_id:
                                    if lot_active_interval == 0:
                                        updateStartDate = True
                                else:
                                    if lot_active_interval == ws2.lot_id.id:
                                        updateStartDate = True
                            if updateStartDate:
                                _logger.info("[mdc.worksheet - refactoring]: * write worksheet: (id: %s) ws.employee_id: %s update end_datetime: from %s to %s."
                                             % (ws.id, ws.employee_id.id, ws.end_datetime, ws.start_datetime))
                                ws.write({'end_datetime': ws.start_datetime})
                                if ws.physical_open:
                                    _logger.info(
                                        "[mdc.worksheet - refactoring]: * write worksheet: (id: %s) ws.employee_id: %s update start_datetime: from %s to %s. Update physical_start_datetime to %s"
                                        % (ws2.id, ws.employee_id.id, ws2.start_datetime, ws.start_datetime, ws.physical_start_datetime))
                                    ws2.write({'start_datetime': ws.start_datetime,
                                               'physical_start_datetime': ws.physical_start_datetime,
                                               'physical_open': ws.physical_open})
                                else:
                                    _logger.info(
                                        "[mdc.worksheet - refactoring]: * write worksheet: (id: %s) ws.employee_id: %s update start_datetime: from %s to %s."
                                        % (ws2.id, ws.employee_id.id, ws2.start_datetime, ws.start_datetime))
                                    ws2.write({
                                        'start_datetime': ws.start_datetime,
                                        'manual_open': ws.manual_open,
                                    })
                                _logger.info("[mdc.worksheet - refactoring]: * delete worksheet: (id: %s) ws.employee_id: %s start_datetime: %s, end_datetime: %s."
                                             % (ws.id, ws.employee_id.id, ws.start_datetime, ws.end_datetime))
                                ws.unlink()
                            else:
                                _logger.info("[mdc.worksheet - refactoring]: * write worksheet: (id: %s) ws.employee_id: %s, start_datetime %s, end_datetime %s, update lot_id: from %s to %s."
                                             % (ws.id, ws.employee_id.id, ws.start_datetime, ws.end_datetime, ws.lot_id.id, lot_active_interval))
                                ws.write({'lot_id': lot_active_interval})
                        else:
                            rs_old_start_datetime = ws.start_datetime  # set in a temp variable de rs.start_datetime before update then
                            _logger.info("[mdc.worksheet - refactoring]: * write worksheet: (id: %s) ws.employee_id: %s, update start_datetime: from %s to %s."
                                         % (ws.id, ws.employee_id.id, ws.start_datetime, end_change_interval))
                            ws.write({'start_datetime': end_change_interval})
                            # if the previous element has end_date = rs_old_start_datetime
                            ws2 = self.search(
                                [('employee_id', '=', ws.employee_id.id), ('end_datetime', '=', rs_old_start_datetime),
                                 ('workstation_id', '=', ws.workstation_id.id), ('shift_id', '=', ws.shift_id.id)])
                            if ws2:
                                # if exists previous element we have to update with end_date = rs_old_start_datetime
                                _logger.info("[mdc.worksheet - refactoring]: * write worksheet:(id: %s)  ws.employee_id: %s update end_datetime: from %s to %s"
                                             % (ws2.id, ws.employee_id.id, ws2.end_datetime, end_change_interval))
                                ws2.write({'end_datetime': end_change_interval})
                            else:
                                _logger.info("[mdc.worksheet - refactoring]: * create worksheet: ws.employee_id: %s, ws.lot_id : %s, ws.start_datetime: %s, ws.end_datetime: %s."
                                             % (ws.employee_id.id, lot_active_interval, rs_old_start_datetime, end_change_interval))
                                self.create({
                                    'employee_id': ws.employee_id.id,
                                    'start_datetime': rs_old_start_datetime,
                                    'end_datetime': end_change_interval,
                                    'lot_id': lot_active_interval,
                                    'workstation_id': ws.workstation_id.id
                                })
                            if ws.end_datetime and end_change_interval > ws.end_datetime:
                                _logger.info("[mdc.worksheet - refactoring]: * create worksheet: ws.employee_id: %s, ws.lot_id : %s, ws.start_datetime: %s, ws.end_datetime: %s"
                                             % (ws.employee_id.id, lot_active_interval, ws.end_datetime, end_change_interval))
                                self.create({
                                    'employee_id': ws.employee_id.id,
                                    'start_datetime': ws.end_datetime,
                                    'end_datetime': end_change_interval,
                                    'lot_id': lot_active_interval,
                                    'workstation_id': ws.workstation_id.id
                                })
        return

    @api.model
    def _listen(self):
        """
        Start listening open and close worksheet events through a websocket connection with RFID server
        :return:
        """
        _logger.info('[mdc.worksheet] Started listener')

        def process_card(card_code, card_datetime):
            # TODO since this process appears to execute in a single (and unique transaction),
            #      a new environment is needed
            # https://www.odoo.com/es_ES/forum/ayuda-1/question/how-to-get-a-new-cursor-on-new-api-on-thread-63441
            with api.Environment.manage():
                with registry(self.env.cr.dbname).cursor() as new_cr:
                    # Create a new environment with new cursor database
                    new_env = api.Environment(new_cr, self.env.uid, self.env.context)

                    ###############################################################################################
                    card = new_env['mdc.card'].search([('name', '=', card_code)])
                    try:
                        if card:
                            if card.employee_id:
                                if card.employee_id.present:
                                    card.employee_id.worksheet_close(card_datetime)
                                    _logger.info(
                                        '[mdc.worksheet] Made close worksheet action for employee with code %s' %
                                        card.employee_id.employee_code)
                                else:
                                    card.employee_id.worksheet_open(card_datetime)
                                    _logger.info(
                                        '[mdc.worksheet] Made open worksheet action for employee with code %s' %
                                        card.employee_id.employee_code)
                            else:
                                raise UserError(_('Card #%s is not an employee one') % card_code)
                        else:
                            raise UserError(_('Unknown card code #%s') % card_code)

                    except UserError as e:
                        _logger.error('[mdc.worksheet] Processing card: %s', e)
                    ###############################################################################################

                    new_env.cr.commit()  # Don't show a invalid-commit in this case
                # You don't need close your cr because is closed when finish "with"
            # You don't need clear caches because is cleared when finish "with"

        def on_message(ws, message):
            """
            ['Event']['user_id']['user_id']  <== card id.
            ['Event']['device_id']['id']  <== device id
            """
            _logger.info('[mdc.worksheet] Received: %s' % message)
            event = ast.literal_eval(message)
            # TODO verify proper event format (e.g. open websocket event is different)
            _logger.info('[mdc.worksheet] Read %s card from %s device!!!' %
                         (event['Event']['user_id']['user_id'], event['Event']['device_id']['id']))
            process_card(event['Event']['user_id']['user_id'], fields.Datetime.now())


        def on_error(ws, error):
            _logger.info('[mdc.worksheet] Websocket error: %s' % error)
            # TODO reconnect? Finish monitoring?

        def on_close(ws):
            _logger.info('[mdc.worksheet] Websocket closed!')

        def on_open(ws):
            _logger.info('[mdc.worksheet] Websocket open')
            ws.send('bs-session-id=%s' % ws_session_data['session_id'])
            _logger.info('[mdc.worksheet] Websocket session id sent')

        # TODO manage server errors and notice them
        ws_session_data = ws_rfid_server.get_session_data(self.env)
        # websocket.enableTrace(True)
        ws_server = websocket.WebSocketApp(ws_session_data['wsapi_url'],
                                           on_message=on_message,
                                           on_error=on_error,
                                           on_close=on_close)
        ws_server.on_open = on_open
        ws_server.run_forever()

        # Only when websocket is closed will end listener. Then, cron job should restart as soon as possible
        _logger.info('[mdc.worksheet] Ended listener')

    @api.model
    def _update_blind_worksheets(self):
        """
        Check new worksheet permissions from RFID server database
        :return:
        """

        def _process_worksheet(Card, data, now, min_secs_worksheet):
            """
            Register an individual worksheet
            :param Card:
            :param data:
            :return:
            """
            card = Card.search([('name', '=', data['usrid'])])
            if card:
                if card.employee_id:
                    worksheet_datetime = datetime.datetime.utcfromtimestamp(data['devdt']).strftime(DF)
                    # -------------------------------------------------------------------------
                    # Repeated physical worksheets
                    last_physical_worksheet_start_datetime = \
                        card.employee_id.last_physical_worksheet_start_datetime or ''
                    last_physical_worksheet_end_datetime = \
                        card.employee_id.last_physical_worksheet_end_datetime or ''
                    last_physical_worksheet_datetime = max(last_physical_worksheet_start_datetime,
                                                           last_physical_worksheet_end_datetime)
                    if last_physical_worksheet_datetime:
                        td = datetime.datetime.strptime(worksheet_datetime, DF) - \
                             datetime.datetime.strptime(last_physical_worksheet_datetime, DF)
                        if td.total_seconds() < min_secs_worksheet:
                            _logger.warning('[mdc.worksheet] Skipped worksheet for user %s@%s'
                                            ' because last physical worksheet (%s) was only %f seconds ago < %d'
                                            % (data['usrid'], worksheet_datetime, last_physical_worksheet_datetime,
                                               td.total_seconds(), min_secs_worksheet))
                            return
                    # -------------------------------------------------------------------------
                    if card.employee_id.present:
                        card.employee_id.worksheet_close(now, worksheet_datetime, physical_close=True)
                        _logger.info(
                            '[mdc.worksheet] Made close worksheet action for employee with code %s' %
                            card.employee_id.employee_code)
                    else:
                        card.employee_id.worksheet_open(now, worksheet_datetime, physical_open=True)
                        _logger.info(
                            '[mdc.worksheet] Made open worksheet action for employee with code %s' %
                            card.employee_id.employee_code)
                else:
                    _logger.warning('[mdc.worksheet] Card #%s is not associated with any employee!!' % data['usrid'])
            else:
                _logger.warning('[mdc.worksheet] Employee #%s not found!!' % data['usrid'])

        _logger.info('[mdc.worksheet] Starting worksheet revision')
        try:
            # TODO retrieve minimum delay for worksheets
            IrConfigParameter = self.env['ir.config_parameter']
            devdt = int(IrConfigParameter.get_param('mdc.rfid_server_last_worksheet_timestamp'))
            # devdt = 1538840634       # Test data

            # TODO if month has already changed since last update, we should also query the previous month table
            today = datetime.datetime.today()
            # today = datetime.datetime.today() - datetime.timedelta(days=30)  # Only for testing purposes
            table = 't_lg%s' % today.strftime('%Y%m')
            _logger.info('[mdc.worksheet] Looking for events on table %s...' % table)

            DbSource = self.env.ref('mdc.base_external_dbsource_rfid_server')
            # TODO WARNING how to close connections??
            # with DbSource.conn_open():
            _logger.info('[mdc.worksheet] Connected to database!')
            res = DbSource.execute(
                query="SELECT devdt, devuid, usrid from {0}"
                      " where usrid <> %(notuser)s and evt>=4097 and evt<=4111"
                      " and devdt >= %(devdt)s order by devdt".format(table),
                execute_params={'notuser': '', 'devdt': devdt})
            _logger.info('[mdc.worksheet] Found %s worksheets with devdt >= %s' % (len(res), devdt))
            if len(res) > 0:
                Card = self.env['mdc.card']
                reader_codes = self.env["mdc.rfid_reader"].get_worksheet_enabled()
                last_timestamp = None
                now = fields.Datetime.now()
                min_secs_worksheet = int(IrConfigParameter.get_param('mdc.rfid_server_min_secs_between_worksheets'))
                for row in res:
                    _logger.info('[mdc.worksheet] Read devdt=%d, devuid=%d, usrid=%s' %
                                 (row['devdt'], row['devuid'], row['usrid']))
                    if str(row["devuid"]) not in reader_codes:
                        _logger.info("[mdc.worksheet] Worksheet skipped due to unauthorized RFID reader (%d)" % row["devuid"])
                        continue
                    # TODO if a particular worksheet fails, the other are processed anyway. The fail worksheet is lost
                    try:
                        _process_worksheet(Card, row, now, min_secs_worksheet)
                    except Exception as e:
                        _logger.info('[mdc.worksheet] Processing worksheet for user %s@%d: %s'
                                     % (row['usrid'], row['devdt'], e))
                    last_timestamp = row['devdt']
                # Last processed worksheet timestamp update, if needed
                if last_timestamp:
                    IrConfigParameter.set_param('mdc.rfid_server_last_worksheet_timestamp', str(last_timestamp))
                    _logger.info('[mdc.worksheet] New last timestamp: %d' % last_timestamp)

        except Exception as e:
            _logger.info('[mdc.worksheet] Worksheet revision: %s', e)

        _logger.info('[mdc.worksheet] Finished worksheet revision')


class LotChkPoint(models.Model):
    """
    Main data for check points and shift
    """
    _name = 'mdc.lot_chkpoint'
    _description = 'Lot active per Check Point and Shift'

    _sql_constraints = [
        ('shift_chkpoint_unique', 'UNIQUE(chkpoint_id,shift_id)',
         _('Combination: Checkpoint & Shift, are unique, and already Exists!')),
    ]

    chkpoint_id = fields.Many2one(
        'mdc.chkpoint',
        string='Checkpoint',
        required=True)
    shift_id = fields.Many2one(
        'mdc.shift',
        string='Shift',
        required=True)
    current_lot_active_id = fields.Many2one(
        'mdc.lot',
        string='Current MO Active Id')
    start_lot_datetime = fields.Datetime(
        string = 'Start MO Active date time'
        )

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

    @api.model
    def create(self, values):
        if 'current_lot_active_id' in values and values['current_lot_active_id']:
            raise UserError(_('You can´t give a lot in create mode'))
        else:
            values['start_lot_datetime'] = None
        if 'start_lot_datetime' in values and values['start_lot_datetime']:
            raise UserError(_('You can´t give a start lot datetime in create mode'))
        return super(LotChkPoint, self).create(values)

    @api.multi
    def unlink(self):
        for r in self:
            if r.current_lot_active_id:
                raise UserError(_('You must to have no lot assigned to delete this record'))
        return super(LotChkPoint, self).unlink()

    @api.multi
    def write(self, values):
        self.ensure_one()
        now = fields.Datetime.now()

        # save new lot on a temp variable
        new_lot_active_id = 0
        if 'current_lot_active_id' in values:
            new_lot_active_id = values['current_lot_active_id']
        else:
            new_lot_active_id = self.current_lot_active_id.id

        # save new and old start-date on a temp variables
        new_start_lot_datetime = ''
        old_start_lot_datetime = ''
        if 'start_lot_datetime' in values:
            # default date = current_date
            if not values['start_lot_datetime']:
                values['start_lot_datetime'] = now
            # when change lot and don´t change date we put default date = current_date
            if 'current_lot_active_id' in values \
                and values['current_lot_active_id'] != self.current_lot_active_id.id \
                and values['start_lot_datetime'] == self.start_lot_datetime:
                values['start_lot_datetime'] = now
            new_start_lot_datetime = values['start_lot_datetime']
            old_start_lot_datetime = self.start_lot_datetime

        if new_start_lot_datetime:
            if new_start_lot_datetime > now:
                raise UserError(_('You can´t give a future start date'))

        #when change lot whe have to do new history records
        # Modifying a current_lot_active and update historic lot_active if it is necessary
        if 'current_lot_active_id' in values and values['current_lot_active_id'] != self.current_lot_active_id.id:
            _logger.info("Change lot: new : %s old: %s"
                         % (values['current_lot_active_id'], self.current_lot_active_id.id))
            if not new_start_lot_datetime:
                new_start_lot_datetime = now
            values['start_lot_datetime'] = new_start_lot_datetime
            old_start_lot_datetime = values['start_lot_datetime']
            self.env['mdc.lot_active'].update_historical(
                chkpoint_id=self.chkpoint_id.id,
                line_id=self.chkpoint_id.line_id,
                shift_id=self.shift_id,
                current_lot_active=self.current_lot_active_id,
                new_lot_active_id=values['current_lot_active_id'],
                start_lot_datetime=values['start_lot_datetime'])

        # if change start data we have do refactoring history of the lot
        if new_start_lot_datetime and old_start_lot_datetime \
                and new_start_lot_datetime != old_start_lot_datetime:
            _logger.info("change start_lot_datetime : new: %s old: %s"
                         % (new_start_lot_datetime, old_start_lot_datetime))
            self.env['mdc.lot_active'].update_start_date(
                chkpoint_id=self.chkpoint_id.id,
                shift_id=self.shift_id,
                new_lot_active_id=new_lot_active_id,
                new_start_lot_datetime=new_start_lot_datetime,
                old_start_lot_datetime=old_start_lot_datetime)

        return super(LotChkPoint, self).write(values)

