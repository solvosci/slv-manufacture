# -*- coding: utf-8 -*-

from odoo import api, models, fields, tools, _


WORKSHEET_TYPES = [
    ('I', 'In'),
    ('O', 'Out'),
]
WORKSHEET_MODES = [
    ('P', 'Physical'),
    ('M', 'Manual'),
]

class RptPhysicalWorksheet(models.Model):
    """
    View-mode model that lists physical worksheets datetime
    """
    _name = 'mdc.rpt_physical_worksheet'
    _description = 'Physical Worksheet Report'
    _order = 'worksheet_date asc, employee_code asc, worksheet_datetime asc'
    _auto = False

    employee_code = fields.Char('Employee Code', readonly=True)
    employee_name = fields.Char('Employee Name', readonly=True)
    workstation_name = fields.Char('Workstation Name', readonly=True)
    shift_code = fields.Char('Shift Code', readonly=True)
    worksheet_date = fields.Date('Worksheet Date', readonly=True)
    worksheet_datetime = fields.Datetime('Worksheet Datetime', readonly=True)
    worksheet_type = fields.Selection(
        selection=WORKSHEET_TYPES,
        string='Worksheet Type', readonly=True)
    worksheet_mode = fields.Selection(
        selection=WORKSHEET_MODES,
        string='Worksheet Mode', readonly=True)

    def init(self):
        tools.drop_view_if_exists(self._cr, self._table)
        # TODO change "worksheet_date" from date(ws.start_datetime) to new field in mdc_worksheet with shift start date
        # while, if there are worksheet with a different start date than the shift start date,
        #           they should filter by worksheet_datetime instead of by worksheet_date
        self._cr.execute("""
                CREATE view %s as 
                    SELECT ws.id, emp.employee_code, emp.name as employee_name, 
                         wst.name as workstation_name, shift.shift_code,
                         date(ws.start_datetime) worksheet_date,  
                         ws.worksheet_datetime, ws.worksheet_type, ws.worksheet_mode
                    FROM (      
                        (SELECT (id*10) id, employee_id, workstation_id, shift_id, start_datetime,
                             start_datetime worksheet_datetime, 'I' worksheet_type, 'P' worksheet_mode
                            FROM mdc_worksheet 
                            WHERE physical_open is True)
                        UNION 
                        (SELECT (id*10+1) id, employee_id, workstation_id, shift_id, start_datetime, 
                             end_datetime worksheet_datetime, 'O' worksheet_type, 'P' worksheet_mode
                            FROM mdc_worksheet
                            WHERE physical_close is True) 
                        UNION
                        (SELECT (id*10) id, employee_id, workstation_id, shift_id, start_datetime, 
                             start_datetime worksheet_datetime, 'I' worksheet_type, 'M' worksheet_mode
                            FROM mdc_worksheet 
                            WHERE manual_open is True)
                        UNION 
                        (SELECT (id*10+1) id, employee_id, workstation_id, shift_id, start_datetime, 
                             end_datetime worksheet_datetime, 'O' worksheet_type, 'M' worksheet_mode
                            FROM mdc_worksheet
                            WHERE manual_close is True) 
                    ) ws 
                    LEFT JOIN hr_employee emp ON emp.id=ws.employee_id
                    LEFT JOIN mdc_workstation wst ON wst.id=ws.workstation_id  
                    LEFT JOIN mdc_shift shift ON shift.id=ws.shift_id
            """ % self._table)
