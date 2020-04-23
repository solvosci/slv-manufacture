# -*- coding: utf-8 -*-
from odoo import fields, tools, models, _
from odoo.addons.mdc.report import report_xlsx
import base64
import tempfile
import datetime, pytz


def formats():
    dic_formats = {}
    dic_formats["dataF"] = {'align': 'center',
                            'bg_color': '#BBDDBB',
                            'num_format': '0'}
    dic_formats["dataY"] = {'align': 'center',
                            'bg_color': '#FFFF00',
                            'num_format': '0'}
    dic_formats["data2dY"] = {'align': 'center',
                              'bg_color': '#FFFF00',
                              'num_format': '0.00'}
    dic_formats["data2dR"] = {'align': 'center',
                              'color': '#FF0000',
                              'num_format': '0.00'}
    return {
        **report_xlsx.formats(),
        **dic_formats
    }


class ReportRptPhysicalWorksheetXlsx(models.AbstractModel):
    _name = 'report.mdc.rpt_physical_worksheet'
    _inherit = 'report.report_xlsx.abstract'

    def convert_UTC_to_TZ(self, utc_dt):
        context_tz = pytz.timezone(
            self.env.context.get('tz') or
            self.env.user.tz or
            self.env['ir.config_parameter'].sudo().get_param(
                'mdc_rpt_physical_worksheet.rpt_physical_worksheet_timezone'))
        return utc_dt + context_tz.utcoffset(utc_dt)

    def generate_xlsx_report(self, workbook, data, rpt_physical_worksheet):
        report_name = "rpt_physical_worksheet"
        sheet = workbook.add_worksheet("Physical Worksheet Report")

        # General sheet style
        sheet.set_landscape()
        sheet.repeat_rows(0,5)
        sheet.hide_gridlines(3)

        # get Formats Dictionary from standard function formats
        f_cells = formats()
        f_title = workbook.add_format(f_cells["title"])
        f_header = workbook.add_format(f_cells ["header"])
        f_header_ind = workbook.add_format(f_cells["header_ind"])
        f_filter = workbook.add_format(f_cells["filter_date"])
        f_data = workbook.add_format(f_cells ["data"])
        f_dataF = workbook.add_format(f_cells["dataF"])
        f_dataY = workbook.add_format(f_cells["dataY"])
        f_dataL = workbook.add_format(f_cells["dataL"])
        f_data2d  = workbook.add_format(f_cells["data2d"])
        f_data2dY= workbook.add_format(f_cells["data2dY"])
        f_data2dR = workbook.add_format(f_cells["data2dR"])

        # Set columns widths
        sheet.set_column('A:AJ', 13)
        sheet.set_column('B:B', 40) # Employee name

        # write logo
        logo_file_name = False
        binary_logo = self.env['res.company'].sudo().search([]).logo_web
        if binary_logo:
            fp = tempfile.NamedTemporaryFile(delete=False)
            fp.write(bytes(base64.b64decode(binary_logo)))
            fp.close()
            logo_file_name = fp.name
        else:
            # TODO enhance default logo path recovery
            logo_file_name = "../addons/manufacture/mdc/report/logo.png"

        sheet.insert_image('A1', logo_file_name, {
            'x_offset': 18, 'y_offset': 18, 'x_scale': 0.9, 'y_scale': 0.5})

        # write Title
        sheet.write(1, 2, _("PHYSICAL WORKSHEET REPORT"), f_title)

        # write Filter
        sheet.write(2, 2, _("Date From:"), f_filter)

        header_row=5
        header_row_str = str(header_row+1)
        # write column header ----------------------------------------
        sheet.write('A' + header_row_str, _("Employee Code"), f_header)
        sheet.write('B' + header_row_str, _("Employee Name"), f_header)
        sheet.write('C' + header_row_str, _("Workstation"), f_header)
        sheet.write('D' + header_row_str, _("Date"), f_header)
        sheet.write('E' + header_row_str, _("Total Hours Corrected"), f_header)
        sheet.write('F' + header_row_str, _("Total Hours only Physical Worksheet"), f_header)
        sheet.write('G' + header_row_str, _("Time In 1"), f_header)
        sheet.write('H' + header_row_str, _("Time Out 1"), f_header_ind)
        sheet.write('I' + header_row_str, _("Time In 2"), f_header)
        sheet.write('J' + header_row_str, _("Time Out 2"), f_header_ind)
        sheet.write('K' + header_row_str, _("Time In 3"), f_header)
        sheet.write('L' + header_row_str, _("Time Out 3"), f_header_ind)
        sheet.write('M' + header_row_str, _("Time In 4"), f_header)
        sheet.write('N' + header_row_str, _("Time Out 4"), f_header_ind)
        sheet.write('O' + header_row_str, _("Time In 5"), f_header)
        sheet.write('P' + header_row_str, _("Time Out 5"), f_header_ind)

        # -------------------------------------------------------
        # write data rows
        row=header_row
        wemployee_code = ''
        wworksheet_date = ''
        wtotal_hours = 0
        wstart_datetime = None
        wend_datetime = None
        wphysical_total_hours = 0
        wphysical_start_datetime = None
        wphysical_end_datetime = None
        wnumcol = 0
        wrowWithErrors=False
        wrowWithManualWS=False
        # Filters ---------
        wstart_date = False
        wend_date = False
        wshift_filter = ''
        wshift_filter_uniq = True
        # -----------------

        # we order the result in case changed the order in the view
        rpt_physical_worksheet_sorted = sorted(rpt_physical_worksheet, key=lambda k: (k['employee_code'], k['worksheet_datetime']))

        for obj in rpt_physical_worksheet_sorted:

            # Filters: ----------------------------------------
            # min a max date
            if wstart_date is False or wstart_date > obj.worksheet_date:
                wstart_date = obj.worksheet_date
            if wend_date is False or wend_date < obj.worksheet_date:
                wend_date = obj.worksheet_date
            # shift
            if wshift_filter == '':
                wshift_filter = obj.shift_code
            # ------------------------------------------------

            # shift Filter
            if wshift_filter != obj.shift_code:
                wshift_filter_uniq = False

            if (wemployee_code != obj.employee_code) or (wworksheet_date != obj.worksheet_date):

                if row > header_row:
                    if wnumcol % 2 == 0:
                        wrowWithErrors=True
                        sheet.write(row, wnumcol+1, "-", f_dataY)
                    #put total_hours of last record
                    sheet.write(row, 4, wtotal_hours, f_data2dY if wrowWithErrors else f_data2d)
                    f_cell = f_data2dY if wrowWithErrors else f_data2dR if wrowWithManualWS else f_data2d
                    sheet.write(row, 5, wphysical_total_hours, f_cell)

                #new record
                row = row + 1

                # direct data from view database
                sheet.write(row, 0, obj.employee_code, f_data)
                sheet.write(row, 1, obj.employee_name, f_dataL)
                sheet.write(row, 2, obj.workstation_name, f_dataL)
                formatted_date = tools.format_date(self.env, obj.worksheet_date)
                sheet.write(row, 3, formatted_date, f_data)

                wtotal_hours = 0
                wphysical_total_hours = 0
                wrowWithErrors = False
                wrowWithManualWS = False
                wnumcol = 5

            # datailed data vars
            wnumcol += 1
            if obj.worksheet_type == 'I':
                wstart_datetime=obj.worksheet_datetime
                if obj.worksheet_mode == 'P':
                    wphysical_start_datetime=obj.worksheet_datetime
                else:
                    wphysical_start_datetime = None
                if wnumcol % 2 == 1:
                    wrowWithErrors=True
                    sheet.write(row, wnumcol, "-", f_dataY)
                    wnumcol += 1
            if obj.worksheet_type == 'O':
                wend_datetime=obj.worksheet_datetime
                if wnumcol % 2 == 0:
                    wrowWithErrors=True
                    sheet.write(row, wnumcol, "-", f_dataY)
                    wstart_datetime = None
                    wphysical_start_datetime = None
                    wnumcol += 1
                else:
                    diff = fields.Datetime.from_string(wend_datetime)\
                           - fields.Datetime.from_string(wstart_datetime)
                    wtotal_hours = wtotal_hours + diff.total_seconds() / 3600
                    if obj.worksheet_mode == 'P' and wphysical_start_datetime:
                        diff = fields.Datetime.from_string(wend_datetime) \
                               - fields.Datetime.from_string(wphysical_start_datetime)
                        wphysical_total_hours = wphysical_total_hours + diff.total_seconds() / 3600


            # formatted_time = fields.Datetime.from_string(obj.worksheet_datetime).strftime('%H:%M.%S')
            formatted_time = self.convert_UTC_to_TZ(fields.Datetime.from_string(obj.worksheet_datetime)).strftime('%H:%M')
            if obj.worksheet_mode == 'M':
                formatted_time = '*'+formatted_time
                wrowWithManualWS = True
            sheet.write(row, wnumcol, formatted_time, f_data if obj.worksheet_type == 'I' else f_dataF)

            wemployee_code = obj.employee_code
            wworksheet_date = obj.worksheet_date

        if row > header_row:
            if wnumcol % 2 == 0:
                wrowWithErrors = True
                sheet.write(row, wnumcol + 1, "-", f_dataY)
            # put total_hours of last record
            sheet.write(row, 4, wtotal_hours, f_data2dY if wrowWithErrors else f_data2d)
            f_cell = f_data2dY if wrowWithErrors else f_data2dR if wrowWithManualWS else f_data2d
            sheet.write(row, 5, wphysical_total_hours, f_cell)

        # write Filter
        datefilter = _("Date From: %s to %s") % (wstart_date, wend_date)
        if wstart_date == wend_date:
            datefilter = _("Date: #%s") % wstart_date
        if wshift_filter_uniq:
            datefilter = datefilter + ' // ' + _("Shift: %s") % wshift_filter
        sheet.write(2, 2, datefilter, f_filter)

        # Final Presentation
        # Select the cells back to image & zoom presentation & split & freeze_panes
        sheet.set_selection('A6')
        sheet.set_zoom(80)
        # sheet.split_panes(60,0,5,0)
