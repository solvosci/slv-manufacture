
import logging

from addons.l10n_in_hr_payroll.report.report_payroll_advice import payroll_advice_report
from odoo import api, fields, models, _
from odoo.exceptions import UserError

import datetime as DT
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DF

_logger = logging.getLogger(__name__)


class Employee(models.Model):
    _inherit = 'hr.employee'

    _sql_constraints = [
        ('employee_code_unique', 'UNIQUE(employee_code)',
         _('Employee code must be unique!')),
    ]

    def _default_employee_code(self):
        last_code = self.search([('employee_code', 'like', 'OPE%')], order='employee_code desc', limit=1)
        code_max_num = 1
        if last_code:
            code_max_num = int(last_code.employee_code[4:]) + 1
        return 'OPE ' + str(code_max_num).zfill(4)

    operator = fields.Boolean('Is operator', required=True, default=False)
    employee_code = fields.Char('Employee code', required=False)
    contract_type_id = fields.Many2one('hr.contract.type', string="Contract Type",
                              default=lambda self: self.env['hr.contract.type'].search([], limit=1))
    workstation_id = fields.One2many(
        'mdc.workstation',
        'current_employee_id')
    worksheets_count = fields.Integer(compute='_compute_worksheets_count', string='Worksheets')
    worksheet_ids = fields.One2many(
        'mdc.worksheet',
        'employee_id')
    present = fields.Boolean(
        'Present',
        readonly=True,
        compute='_compute_present',
        store=True)
    worksheet_end_datetime = fields.Datetime(
        'Worksheet End Datetime',
        readonly=True,
        compute='_compute_worksheet_data',
        store=True)
    worksheet_status_start_datetime = fields.Datetime(
        'Worksheet Status Start Datetime',
        readonly=True,
        compute='_compute_worksheet_data',
        store=True)
    worksheet_status_data = fields.Char(
        'Worksheet Status data',
        readonly=True,
        compute='_compute_worksheet_data',
        store=True)
    last_physical_worksheet_start_datetime = fields.Datetime(
        'Last physical worksheet start datetime',
        readonly=True,
        compute='_compute_last_physical_worksheet_start_datetime',
        store=True
    )
    last_physical_worksheet_end_datetime = fields.Datetime(
        'Last physical worksheet end datetime',
        readonly=True,
        compute='_compute_last_physical_worksheet_end_datetime',
        store=True
    )

    def _compute_worksheets_count(self):
        """
        # read_group as sudo, since worksheet count is displayed on form view
        worksheet_data = self.env['mdc.worksheet'].sudo().read_group([('employee_id', 'in', self.ids)], ['employee_id'],
                                                                  ['employee_id'])
        result = dict((data['employee_id'][0], data['employee_id_count']) for data in worksheet_data)
        for employee in self:
            employee.worksheets_count = result.get(employee.id, 0)
        """
        # TODO check count performance when growing data. If decreases, use the code above
        for employee in self:
            employee.worksheets_count = len(employee.worksheet_ids)

    @api.multi
    @api.depends('worksheet_ids.end_datetime')
    def _compute_present(self):
        """
        worksheet_data = self.env['mdc.worksheet'].sudo().read_group(
            [('employee_id', 'in', self.ids), ('end_datetime', '=', False)],
            ['employee_id'],
            ['employee_id'])
        result = dict((data['employee_id'][0], data['employee_id_count']) for data in worksheet_data)
        for employee in self:
            employee.present = True if result.get(employee.id, 0) > 0 else False
        """
        # TODO check filtered performance when growing data. If decreases, use the code above
        for employee in self:
            employee.present = len(employee.worksheet_ids.filtered(lambda r: r.end_datetime is False)) > 0

    @api.multi
    @api.depends('worksheet_ids.end_datetime')
    def _compute_worksheet_data(self):
        # TODO check filtered performance when growing data
        for employee in self:
            # compute the last end datetime (to use to validate on create and write a worksheet)
            last_end_datetime = None
            # compute the last start datetime (to built worksheet status = last start date opened + lot + workstation)
            last_start_datetime = None
            worksheet_data_status = None
            # to do this we need de last worksheet of te employee
            we = self.env['mdc.worksheet'].search([('employee_id', '=', employee.id)]
                                                  , order='start_datetime desc', limit=2)
            for ws in we:
                if last_end_datetime is None and ws.end_datetime is not False:
                    last_end_datetime = ws.end_datetime
                if worksheet_data_status is None and ws.end_datetime is False:
                    last_start_datetime = ws.start_datetime
                    worksheet_data_status = '%s - %s ' % (ws.lot_id.name or '', ws.workstation_id.name or '')

            # set the calculated values
            employee.worksheet_end_datetime = last_end_datetime
            employee.worksheet_status_start_datetime = last_start_datetime
            employee.worksheet_status_data = worksheet_data_status

    @api.multi
    @api.depends('worksheet_ids.end_datetime')
    def _compute_last_physical_worksheet_start_datetime(self):
        for employee in self:
            physical_open_worksheets = employee.worksheet_ids.filtered(lambda r: r.physical_open)
            if physical_open_worksheets:
                employee.last_physical_worksheet_start_datetime = physical_open_worksheets[-1].physical_start_datetime

    @api.multi
    @api.depends('worksheet_ids.end_datetime')
    def _compute_last_physical_worksheet_end_datetime(self):
        for employee in self:
            physical_closed_worksheets = employee.worksheet_ids.filtered(lambda r: r.physical_close)
            if physical_closed_worksheets:
                employee.last_physical_worksheet_end_datetime = physical_closed_worksheets[-1].physical_end_datetime

    @api.model
    def create(self, values):
        _logger.info("[hr.employee] Employee_create")

        if values.get('operator') and not values.get('employee_code'):
            values['employee_code'] = self._default_employee_code()

        return super(Employee, self).create(values)

    @api.multi
    def write(self, values):
        self.ensure_one()
        if 'operator' in values:
            if values['operator'] and not self.employee_code and not 'employee_code' in values:
                # Employee is now an operator and his employee code is not set
                values['employee_code'] = self._default_employee_code()
            if not values['operator']:
                # Employee is no longer an operator, then employee code and contract type must be removed
                values['employee_code'] = False
                values['contract_type_id'] = False
        else:
            if 'employee_code' in values and not values['employee_code']:
                raise UserError(_("It's not allowed to delete employee code for an operator. "
                                  "If you want to set an automatic code, first unset operator check and save"))

        return super(Employee, self).write(values)

    def _check_worksheet_permissions(self):
        """
        perm_group_id = self.env.ref('group_mdc_office_worker').id
        my_group_ids = self.env.user.groups_id.ids
        if perm_group_id not in my_group_ids:
            raise UserError(_('You are not allowed to open/close worksheets'))
        """
        return self.env.user.has_group('mdc.group_mdc_office_worker')

    @api.multi
    def worksheet_open(self, start_datetime, physical_start_datetime=False,
                       physical_open=False, manual_open=False):
        self.ensure_one()
        self._check_worksheet_permissions()
        if self.present:
            raise UserError(_('Cannot create open worksheet: employee %s is already present') % self.employee_code)
        self.env['mdc.worksheet'].sudo().create({
            'start_datetime': start_datetime,
            'employee_id': self.id,
            'physical_start_datetime': physical_start_datetime,
            'physical_open': physical_open,
            'manual_open': manual_open,
        })

    @api.multi
    def worksheet_close(self, end_datetime, physical_end_datetime=False,
                        physical_close=False, manual_close=False):
        self.ensure_one()
        self._check_worksheet_permissions()
        if not self.present:
            raise UserError(_('Cannot create close worksheet: employee %s is not present') % self.employee_code)
        self.worksheet_ids.filtered(lambda r: r.end_datetime is False).sudo().write({
            'end_datetime': end_datetime,
            'physical_end_datetime': physical_end_datetime,
            'physical_close': physical_close,
            'manual_close': manual_close,
        })

        # TODO check filtered performance when growing data. If decreases, use the code above
        """
        Worksheet = self.env['mdc.worksheet'].search(
            [('end_datetime', '=', False),
             ('employee_id', '=', self.id)])
        Worksheet.write({'end_datetime': self.end_datetime})
        """

    def massive_worksheet_open(self):
        Wizard = self.env['hr.employee.massworksheetopen.wizard']
        new = Wizard.create({
            'employee_ids': [(6, False, self._context['active_ids'])]
        })
        return {
            'name': 'Massive worksheet open',
            'res_model': 'hr.employee.massworksheetopen.wizard',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': new.id,
            'target': 'new',
            'type': 'ir.actions.act_window'
        }

    def massive_worksheet_close(self):
        Wizard = self.env['hr.employee.massworksheetclose.wizard']
        new = Wizard.create({
            'employee_ids': [(6, False, self._context['active_ids'])]
        })
        return {
            'name': 'Massive worksheet close',
            'res_model': 'hr.employee.massworksheetclose.wizard',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': new.id,
            'target': 'new',
            'type': 'ir.actions.act_window'
        }


class EmployeeMassWorksheetOpen(models.TransientModel):
    _name = 'hr.employee.massworksheetopen.wizard'
    _description = 'Employee massive worksheet open wizard'

    def _default_date(self):
        #return fields.Datetime.from_string(fields.Datetime.now())
        return fields.Datetime.now()

    start_datetime = fields.Datetime(
        'Start Datetime',
        required=True,
        default=_default_date)
    employee_ids = fields.Many2many(
        'hr.employee',
        string='Employees')

    @api.model
    def create(self, values):
        # TODO
        return super(EmployeeMassWorksheetOpen, self).create(values)

    def action_save(self):
        self.ensure_one()
        for employee in self.employee_ids:
            employee.worksheet_open(self.start_datetime, manual_open=True)

    def action_cancel(self):
        return True


class EmployeeMassWorksheetClose(models.TransientModel):
    _name = 'hr.employee.massworksheetclose.wizard'
    _description = 'Employee massive worksheet close wizard'

    def _default_date(self):
        #return fields.Datetime.from_string(fields.Datetime.now())
        return fields.Datetime.now()

    end_datetime = fields.Datetime(
        'End Datetime',
        required=True,
        default=_default_date)
    employee_ids = fields.Many2many(
        'hr.employee',
        string='Employees')

    @api.model
    def create(self, values):
        # TODO
        return super(EmployeeMassWorksheetClose, self).create(values)

    def action_save(self):
        self.ensure_one()
        for employee in self.employee_ids:
            employee.worksheet_close(self.end_datetime, manual_close=True)

    def action_cancel(self):
        return True
