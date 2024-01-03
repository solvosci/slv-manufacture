# -*- coding: utf-8 -*-
from odoo import tools, models, _
import base64
import tempfile
import datetime

def formats():
    # Python dictionary with cells formats and styles for XLSX reports
    dic_formats={}
    dic_formats["title"] = {'bold': True, 'size': 30}
    dic_formats["filter"] = {'bold': True,
                                  'font_color': '#004080',
                                  'size': 16}
    dic_formats["filter_date"] = {'bold': True,
                             'font_color': '#004080',
                             'size': 16,
                             'num_format': '[$-x-sysdate]dddd, mmmm dd, aaaa'}
    dic_formats["header"] = {'bold': True,
                             'font_color': '#004080',
                             'bottom': True,
                             'top': True,
                             'text_wrap': True,
                             'align': 'center',
                             'size': 12}
    dic_formats["header_ind"] = {'bold': True,
                             'font_color': '#004080',
                             'bg_color': '#BBDDBB',
                             'bottom': True,
                             'top': True,
                             'text_wrap': True,
                             'align': 'center',
                             'size': 12}
    dic_formats["header_ind_old"] = {'bold': True,
                             'font_color': '#004080',
                             'bg_color': '#DDDDDD',
                             'bottom': True,
                             'top': True,
                             'text_wrap': True,
                             'align': 'center',
                             'size': 12}
    dic_formats["footer"] = {'bold': True,
                             'font_color': '#003060',
                             'bg_color': '#CCCCCC',
                             'bottom': True,
                             'top': True,
                             'text_wrap': True,
                             'align': 'center',
                             'size': 12,
                             'num_format': '0.00'}
    dic_formats["footer_perc"] = {'bold': True,
                             'font_color': '#003060',
                             'bg_color': '#CCCCCC',
                             'bottom': True,
                             'top': True,
                             'text_wrap': True,
                             'align': 'center',
                             'size': 12,
                             'num_format': '0.00%'}
    dic_formats["footer_int"] = {'bold': True,
                             'font_color': '#003060',
                             'bg_color': '#CCCCCC',
                             'bottom': True,
                             'top': True,
                             'text_wrap': True,
                             'align': 'center',
                             'size': 12,
                             'num_format': '0'}
    dic_formats["data"] = {'align': 'center',
                             'num_format': '0'}
    dic_formats["dataL"] = {'align': 'left',
                           'num_format': '0'}
    dic_formats["data2d"] = {'align': 'center',
                             'num_format': '0.00'}
    dic_formats["data3d"] = {'align': 'center',
                             'num_format': '0.000'}
    dic_formats["percent"] = {'align': 'center',
                             'num_format': '0.00%'}
    return dic_formats

class ReportRptStageManufacturingXlsx(models.AbstractModel):
    _name = 'report.mdc.rpt_stage_manufacturing'
    _inherit = 'report.report_xlsx.abstract'
    _description = "MDC RPT Stage Manufacturing XLSX"

    def generate_xlsx_report(self, workbook, data, rpt_stage_manufacturing):    
        report_name = "rpt_stage_manufacturing"
        sheet = workbook.add_worksheet("Stage Manufacturing Report")

        # retrieve rpt_hide_shift_change_data parameter
        hide_shift_data = self.env['ir.config_parameter'].sudo().get_param(
            'mdc.rpt_hide_shift_change_data')

        # General sheet style
        sheet.set_landscape()
        sheet.repeat_rows(0,5)
        sheet.hide_gridlines(3)

        # get Formats Dictionary from standard function formats
        f_cells = formats()
        f_title = workbook.add_format(f_cells["title"])
        f_header = workbook.add_format(f_cells["header"])
        f_header_ind = workbook.add_format(f_cells["header_ind"])
        f_header_ind_old = workbook.add_format(f_cells["header_ind_old"])
        f_filter = workbook.add_format(f_cells["filter_date"])
        f_percent = workbook.add_format(f_cells["percent"])
        f_data = workbook.add_format(f_cells["data"])
        f_dataL = workbook.add_format(f_cells["dataL"])
        f_data2d = workbook.add_format(f_cells["data2d"])
        f_data3d = workbook.add_format(f_cells["data3d"])
        f_footer = workbook.add_format(f_cells["footer"])
        f_footer_perc = workbook.add_format(f_cells["footer_perc"])
        f_footer_int = workbook.add_format(f_cells["footer_int"])

        # Set columns widths
        sheet.set_column('A:T', 13)
        sheet.set_column('F:F', 40)  # Workstation name
        sheet.set_column('H:H', 16)  # Client name
        sheet.set_column('T:T', 40)  # Observations = lot_descrip

        # write logo
        logo_file_name = False
        # binary_logo = self.env.company.logo_web
        binary_logo = self.env.company.logo_web
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
        sheet.write(1, 2, _("STAGE MANUFACTURING REPORT"), f_title)

        # write Filter
        sheet.write(2, 2, _("Date From:"), f_filter)

        header_row = 5
        header_row_str = str(header_row + 1)
        # write column header ----------------------------------------
        sheet.write('A' + header_row_str, _("Lot name"), f_header)  # - 1
        sheet.write('B' + header_row_str, _("Product"), f_header)
        sheet.write('C' + header_row_str, _("Shift Code"), f_header)
        sheet.write('D' + header_row_str, _("Line Code"), f_header)
        sheet.write('E' + header_row_str, _("Stage Name"), f_header)
        sheet.write('F' + header_row_str, _("Workstation"), f_header)  # - 6
        sheet.write('G' + header_row_str, _("Employee Code"), f_header)
        sheet.write('H' + header_row_str, _("Employee  Name"), f_header)
        sheet.write('I' + header_row_str, _("Gross Weight"), f_header)
        sheet.write('J' + header_row_str, _("Backs"), f_header)
        sheet.write('K' + header_row_str, _("Crumbs"), f_header)  # - 11
        sheet.write('L' + header_row_str, _("Pieces"), f_header)
        sheet.write('M' + header_row_str, _("Quality"), f_header)
        sheet.write('N' + header_row_str, _("% Backs"), f_header)
        sheet.write('O' + header_row_str, _("% Crumbs"), f_header)
        sheet.write('P' + header_row_str, _("% Pieces"), f_header)  # - 16
        sheet.write('Q' + header_row_str, _("% Total Yield"), f_header)
        sheet.write('R' + header_row_str, _("Speed (MIN/KG)"), f_header)
        sheet.write('S' + header_row_str, _("Time (H)"), f_header)
        sheet.write('T' + header_row_str, _("Observations"), f_header) # - 20
        # -------------------------------------------------------

        # TODO alternate dict list with almost grouped data (still problems with product and date)

        # write data rows
        row = header_row
        wlot_name = ''
        wemployee_code = ''
        wworkstation_name = ''
        # Filters ---------
        wstart_date = False
        wend_date = False
        wlot_filter = ''
        wshift_filter = ''
        # -----------------

        for obj in rpt_stage_manufacturing:

            # Filters: ----------------------------------------
            # min a max date
            if wstart_date is False or wstart_date > obj.create_date:
                wstart_date = obj.create_date
            if wend_date is False or wend_date < obj.create_date:
                wend_date = obj.create_date
            # lot
            if wlot_filter == '':
                wlot_filter = obj.lot_name
                product_name = obj.product_id.name_get()[0][1]
            # shift
            if wshift_filter == '':
                wshift_filter = obj.shift_code
            # ------------------------------------------------

            # shift Filter
            if wshift_filter != obj.shift_code:
                wshift_filter_uniq = False

            if (wlot_name != obj.lot_name) or (wemployee_code != obj.employee_code) or (
                    wworkstation_name != obj.workstation_name):
                # lot Filter
                if wlot_filter != obj.lot_name:
                    wlot_filter_uniq = False

                row = row + 1

                # direct data from view database
                sheet.write(row, 0, obj.lot_name, f_data)
                sheet.write(row, 1, obj.product_id.name, f_data)
                sheet.write(row, 2, obj.shift_code, f_data)
                sheet.write(row, 3, obj.line_code, f_data)
                sheet.write(row, 4, obj.stage_name, f_data)
                sheet.write(row, 5, obj.workstation_name, f_data)
                sheet.write(row, 6, obj.employee_code, f_data)
                sheet.write(row, 7, obj.employee_name, f_data)
                sheet.write(row, 8, obj.gross_weight, f_data2d)
                sheet.write(row, 9, obj.product_weight, f_data2d)
                sheet.write(row, 10, obj.sp1_weight, f_data2d)
                sheet.write(row, 11, obj.sp2_weight, f_data2d)
                sheet.write(row, 12, obj.quality_weight, f_data)
                sheet.write(row, 18, obj.total_hours, f_data2d)

                # formulation columns
                sheet.write_formula(row, 13,        # - % Backs
                    '=IF(I' + str(row + 1) + '= 0, 0, J' + str(row + 1) + '/I' + str(row + 1) + ')',
                f_percent)
                sheet.write_formula(row, 14,        # - % Crumbs
                    '=IF(I' + str(row + 1) + '= 0, 0, K' + str(row + 1) + '/I' + str(row + 1) + ')',
                f_percent)
                sheet.write_formula(row, 15,        # - % Pieces
                    '=IF(I' + str(row + 1) + '= 0, 0, L' + str(row + 1) + '/I' + str(row + 1) + ')',
                f_percent)
                sheet.write_formula(row, 16,        # - % Total Yield
                    '=IF(I' + str(row + 1) + '= 0, 0, (J' + str(row + 1) + '+K' + str(row + 1) + '+L' + str(row + 1) + ')/I' + str(row + 1) + ')',
                f_percent)  
                sheet.write_formula(row, 17,        # - Speed
                    '=IF(I' + str(row + 1) + '= 0, 0, (S' + str(row + 1) + ' * 60)/I' + str(row + 1) + ')',
                f_data2d)

            # Final Footer Row ------------------------------------------
            for numcol in range(0, 20):
                sheet.write(row + 1, numcol, '', f_footer)
            sheet.write_formula(
                row + 1, 8, '=SUM(I' + str(header_row + 1) + ':I' + str(row + 1) + ')',
            f_footer)
            sheet.write_formula(
                row + 1, 9, '=SUM(J' + str(header_row + 1) + ':J' + str(row + 1) + ')',
            f_footer)
            sheet.write_formula(
                row + 1, 10, '=SUM(K' + str(header_row + 1) + ':K' + str(row + 1) + ')',
            f_footer)
            sheet.write_formula(
                row + 1, 11, '=SUM(L' + str(header_row + 1) + ':L' + str(row + 1) + ')',
            f_footer)
            sheet.write_formula(                                # - Quality
                row + 1, 12,
                '=IF(I' + str(row + 2) + '= 0, 0, SUMPRODUCT(M' + str(header_row + 1) + ':M' + str(row + 1) + ', I' + str(header_row + 1) + ':I' + str(row + 1) + ')/I' + str(row + 2) + ')',
            f_footer_int)
            sheet.write_formula(                                # - % Backs
                row + 1, 13,
                '=IF(I' + str(row + 2) + '= 0, 0, J' + str(row + 2) + '/I' + str(row + 2) + ')',
            f_footer)
            sheet.write_formula(
                row + 1, 14, '=AVERAGE(O' + str(header_row + 1) + ':O' + str(row + 1) + ')',
            f_footer)
            sheet.write_formula(
                row + 1, 15, '=AVERAGE(P' + str(header_row + 1) + ':P' + str(row + 1) + ')',
            f_footer)
            sheet.write_formula(                                # - % Total Yield
                row + 1, 16,
                '=IF(I' + str(row + 2) + '= 0, 0, (J' + str(row + 2) + '+K' + str(row + 2) + '+L' + str(row + 2) + ')/I' + str(row + 2) + ')',
            f_footer)
            sheet.write_formula(                                # - Speed
                row + 1, 17,  '=IF(I' + str(row + 2) + '= 0, 0, (S' + str(row + 2) + ' * 60)/I' + str(row + 2) + ')',
            f_footer)
            sheet.write_formula(
                row + 1, 18, '=SUM(S' + str(header_row + 1) + ':S' + str(row + 1) + ')',
            f_footer)

            # Write Filter -----------------------------------------------
            sheet.write(2, 2, datetime.datetime.now(), f_filter)

        # Final Presentation
        # Select the cells back to image & zoom presentation & split & freeze_panes
        sheet.set_selection('A6')
        sheet.set_zoom(80)
        # sheet.split_panes(60,0,5,0)


class ReportRptLineManufacturingXlsx(models.AbstractModel):
    _name = 'report.mdc.rpt_line_manufacturing'
    _inherit = 'report.report_xlsx.abstract'
    _description = "MDC RPT Line Manufacturing XLSX"

    def generate_xlsx_report(self, workbook, data, rpt_line_manufacturing):
        report_name = "rpt_line_manufacturing"
        sheet = workbook.add_worksheet("Line Manufacturing Report")

        # retrieve rpt_hide_shift_change_data parameter
        hide_shift_data = self.env['ir.config_parameter'].sudo().get_param(
            'mdc.rpt_hide_shift_change_data')

        # General sheet style
        sheet.set_landscape()
        sheet.repeat_rows(0,5)
        sheet.hide_gridlines(3)

        # get Formats Dictionary from standard function formats
        f_cells = formats()
        f_title = workbook.add_format(f_cells["title"])
        f_header = workbook.add_format(f_cells ["header"])
        f_header_ind = workbook.add_format(f_cells["header_ind"])
        f_header_ind_old = workbook.add_format(f_cells["header_ind_old"])
        f_filter = workbook.add_format(f_cells["filter_date"])
        f_percent = workbook.add_format(f_cells ["percent"])
        f_data = workbook.add_format(f_cells ["data"])
        f_dataL = workbook.add_format(f_cells["dataL"])
        f_data2d = workbook.add_format(f_cells["data2d"])
        f_data3d = workbook.add_format(f_cells["data3d"])
        f_footer = workbook.add_format(f_cells["footer"])
        f_footer_perc = workbook.add_format(f_cells["footer_perc"])
        f_footer_int = workbook.add_format(f_cells["footer_int"])

        # Set columns widths
        sheet.set_column('A:N', 13)
        sheet.set_column('N:N', 40)  # Observations = lot_descrip
        if hide_shift_data:
            sheet.set_column('R:T', 0, None, {'hidden': 1})

        # write logo
        logo_file_name = False
        # binary_logo = self.env.company.logo_web
        binary_logo = self.env.company.logo_web
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
        sheet.write(1, 2, _("LINE MANUFACTURING REPORT"), f_title)

        # write Filter
        sheet.write(2, 2, _("Date From:"), f_filter)

        header_row=5
        header_row_str = str(header_row+1)
        # write column header ----------------------------------------
        sheet.write('A' + header_row_str, _("Lot name"), f_header)  # - 0
        sheet.write('B' + header_row_str, _("Product"), f_header)
        sheet.write('C' + header_row_str, _("Shift Code"), f_header)
        sheet.write('D' + header_row_str, _("Line Code"), f_header)
        sheet.write('E' + header_row_str, _("Gross Weight"), f_header)
        sheet.write('F' + header_row_str, _("Backs"), f_header) # - 5
        sheet.write('G' + header_row_str, _("Crumbs"), f_header)
        sheet.write('H' + header_row_str, _("Pieces"), f_header)
        sheet.write('I' + header_row_str, _("Quality"), f_header)
        sheet.write('J' + header_row_str, _("% Backs"), f_header)
        sheet.write('K' + header_row_str, _("% Crumbs"), f_header)  # - 10
        sheet.write('L' + header_row_str, _("% Pieces"), f_header)
        sheet.write('M' + header_row_str, _("Time (H)"), f_header)
        sheet.write('N' + header_row_str, _("Observations"), f_header)  # - 13
        # -------------------------------------------------------

        # TODO alternate dict list with almost grouped data (still problems with product and date)

        # write data rows
        row=header_row

        # Filters ---------
        wstart_date = False
        wend_date = False
        wlot_filter = ''
        # -----------------

        for obj in rpt_line_manufacturing:

            # Filters: ----------------------------------------
            # min a max date
            if wstart_date is False or wstart_date > obj.create_date:
                wstart_date = obj.create_date
            if wend_date is False or wend_date < obj.create_date:
                wend_date = obj.create_date
            # lot
            if wlot_filter == '':
                wlot_filter = obj.lot_name
                product_name = obj.product_id.name_get()[0][1]
            # shift
            # if wshift_filter == '':
            #     wshift_filter = obj.shift_code
            # wgross_frozen += obj.gross_weight_reference
            # ------------------------------------------------

            # shift Filter
            # if wshift_filter != obj.shift_code:
            #     wshift_filter_uniq = False

            # if (wlot_name != obj.lot_name) or (wemployee_code != obj.employee_code) or (wworkstation_name != obj.workstation_name):
            #     # lot Filter
            #     if wlot_filter != obj.lot_name:
            #         wlot_filter_uniq = False

                row = row + 1

                # direct data from view database
                sheet.write(row, 0, obj.lot_name, f_data)
                sheet.write(row, 1, obj.product_id.name, f_data)
                sheet.write(row, 2, obj.shift_code, f_data)
                sheet.write(row, 3, obj.line_code, f_data)
                sheet.write(row, 4, obj.final_gross_weight, f_data2d)
                sheet.write(row, 5, obj.product_weight, f_data2d)
                sheet.write(row, 6, obj.sp1_weight, f_data2d)
                sheet.write(row, 7, obj.sp2_weight, f_data2d)
                sheet.write(row, 8, obj.quality_weight, f_data2d)
                sheet.write(row, 12, obj.total_hours, f_data)

                # formulation columns
                sheet.write_formula(row, 9,         # - % Backs
                    '=IF(E' + str(row + 1) + '= 0, 0, F' + str(row + 1) + '/E' + str(row + 1) + ')',
                f_percent)
                sheet.write_formula(row, 10,        # - % Crumbs
                    '=IF(E' + str(row + 1) + '= 0, 0, G' + str(row + 1) + '/E' + str(row + 1) + ')',
                f_percent)
                sheet.write_formula(row, 11,        # - % Pieces
                    '=IF(E' + str(row + 1) + '= 0, 0, H' + str(row + 1) + '/E' + str(row + 1) + ')',
                f_percent)


                # Final Footer Row ------------------------------------------
                for numcol in range(0, 14):
                    sheet.write(row + 1, numcol, '', f_footer)
                sheet.write_formula(                                # - Quality
                    row + 1, 12,
                    '=IF(I' + str(row + 2) + '= 0, 0, SUMPRODUCT(M' + str(header_row + 1) + ':M' + str(row + 1) + '; I' + str(header_row + 1) + ':I' + str(row + 1) + ')/I' + str(row + 2) + ')',
                f_footer_int)
                sheet.write_formula(                                # - % Backs
                    row + 1, 9,
                    '=IF(E' + str(row + 2) + '= 0, 0, F' + str(row + 2) + '/E' + str(row + 2) + ')',
                f_footer_perc)
                sheet.write_formula(
                    row + 1, 10, '=AVERAGE(J' + str(header_row + 1) + ':J' + str(row + 1) + ')',
                f_footer_perc)
                sheet.write_formula(
                    row + 1, 11, '=AVERAGE(K' + str(header_row + 1) + ':K' + str(row + 1) + ')',
                f_footer_perc)
                sheet.write_formula(
                    row + 1, 12, '=SUM(L' + str(header_row + 1) + ':L' + str(row + 1) + ')',
                f_footer_int)



            # Write Filter -----------------------------------------------
            sheet.write(2, 2, datetime.datetime.now(), f_filter)

        # Final Presentation
        # Select the cells back to image & zoom presentation & split & freeze_panes
        sheet.set_selection('A6')
        sheet.set_zoom(80)
        # sheet.split_panes(60,0,5,0)


class ReportRptEmployeeYieldXlsx(models.AbstractModel):
    _name = 'report.mdc.rpt_employee_yield'
    _inherit = 'report.report_xlsx.abstract'
    _description = "MDC RPT Employee Yield XLSX"

    def generate_xlsx_report(self, workbook, data, rpt_employee_yield):    
        report_name = "rpt_employee_yield"
        sheet = workbook.add_worksheet("Employee Yield Report")

        # retrieve rpt_hide_shift_change_data parameter
        hide_shift_data = self.env['ir.config_parameter'].sudo().get_param(
            'mdc.rpt_hide_shift_change_data')

        # General sheet style
        sheet.set_landscape()
        sheet.repeat_rows(0,5)
        sheet.hide_gridlines(3)

        # get Formats Dictionary from standard function formats
        f_cells = formats()
        f_title = workbook.add_format(f_cells["title"])
        f_header = workbook.add_format(f_cells["header"])
        f_header_ind = workbook.add_format(f_cells["header_ind"])
        f_header_ind_old = workbook.add_format(f_cells["header_ind_old"])
        f_filter = workbook.add_format(f_cells["filter_date"])
        f_percent = workbook.add_format(f_cells["percent"])
        f_data = workbook.add_format(f_cells["data"])
        f_dataL = workbook.add_format(f_cells["dataL"])
        f_data2d = workbook.add_format(f_cells["data2d"])
        f_data3d = workbook.add_format(f_cells["data3d"])
        f_footer = workbook.add_format(f_cells["footer"])
        f_footer_perc = workbook.add_format(f_cells["footer_perc"])
        f_footer_int = workbook.add_format(f_cells["footer_int"])

        # Set columns widths
        sheet.set_column('A:M', 13)
        sheet.set_column('B:B', 40)  # Employee Name
        sheet.set_column('M:M', 40)  # Observations = lot_descrip
        if hide_shift_data:
            sheet.set_column('R:T', 0, None, {'hidden': 1})

        # write logo
        logo_file_name = False
        # binary_logo = self.env.company.logo_web
        binary_logo = self.env.company.logo_web
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
        sheet.write(1, 2, _("EMPLOYEE YIELD REPORT"), f_title)

        # write Filter
        sheet.write(2, 2, _("Date From:"), f_filter)

        header_row = 5
        header_row_str = str(header_row + 1)
        # write column header ----------------------------------------
        sheet.write('A' + header_row_str, _("Employee Code"), f_header)
        sheet.write('B' + header_row_str, _("Employee Name"), f_header)
        sheet.write('C' + header_row_str, _("Shift Code"), f_header)
        sheet.write('D' + header_row_str, _("Line Code"), f_header)
        sheet.write('E' + header_row_str, _("Stage Name"), f_header)
        sheet.write('F' + header_row_str, _("Product"), f_header)
        sheet.write('G' + header_row_str, _("Gross Weight"), f_header)
        sheet.write('H' + header_row_str, _("Backs"), f_header)
        sheet.write('I' + header_row_str, _("Crumbs"), f_header)  # - 10
        sheet.write('J' + header_row_str, _("Pieces"), f_header)
        sheet.write('K' + header_row_str, _("Quality"), f_header)
        sheet.write('L' + header_row_str, _("Time (H)"), f_header)        
        sheet.write('M' + header_row_str, _("Observations"), f_header)
        # -------------------------------------------------------

        # TODO alternate dict list with almost grouped data (still problems with product and date)

        # write data rows
        row = header_row
        # Filters ---------
        wstart_date = False
        wend_date = False
        # -----------------

        for obj in rpt_employee_yield:

            # Filters: ----------------------------------------
            # min a max date
            if wstart_date is False or wstart_date > obj.create_date:
                wstart_date = obj.create_date
            if wend_date is False or wend_date < obj.create_date:
                wend_date = obj.create_date

                row = row + 1

                # direct data from view database
                sheet.write(row, 0, obj.employee_code, f_data)
                sheet.write(row, 1, obj.employee_name, f_data)
                sheet.write(row, 2, obj.shift_code, f_data)
                sheet.write(row, 3, obj.line_code, f_dataL)
                sheet.write(row, 4, obj.stage_name, f_dataL)
                sheet.write(row, 5, obj.product_id.name, f_data2d)
                sheet.write(row, 6, obj.gross_weight, f_data2d)
                sheet.write(row, 7, obj.product_weight, f_data2d)
                sheet.write(row, 8, obj.sp1_weight, f_data2d)
                sheet.write(row, 9, obj.sp2_weight, f_data2d)
                sheet.write(row, 10, obj.quality_weight, f_data)
                sheet.write(row, 11, obj.total_hours, f_data)
                        # Final Footer Row ------------------------------------------
            for numcol in range(0, 13):
                sheet.write(row + 1, numcol, '', f_footer)
            sheet.write_formula(            # - Gross Weight
                row + 1, 6, '=SUM(G' + str(header_row + 1) + ':G' + str(row + 1) + ')',
            f_footer)
            sheet.write_formula(            # - Backs
                row + 1, 7, '=SUM(H' + str(header_row + 1) + ':H' + str(row + 1) + ')',
            f_footer)
            sheet.write_formula(            # - Crumbs
                row + 1, 8, '=SUM(I' + str(header_row + 1) + ':I' + str(row + 1) + ')',
            f_footer)
            sheet.write_formula(            # - Pieces
                row + 1, 9, '=SUM(J' + str(header_row + 1) + ':J' + str(row + 1) + ')',
            f_footer)
            sheet.write_formula(            # - Quality
                row + 1, 10,
                '=IF(G' + str(row + 2) + '= 0, 0, SUMPRODUCT(K' + str(header_row + 1) + ':K' + str(row + 1) + ', G' + str(header_row + 1) + ':G' + str(row + 1) + ')/G' + str(row + 2) + ')',
            f_footer_int)
            sheet.write_formula(
                row + 1, 11, '=SUM(L' + str(header_row + 1) + ':L' + str(row + 1) + ')',
            f_footer_int)



            # Write Filter -----------------------------------------------
            sheet.write(2, 2, datetime.datetime.now(), f_filter)

        # Final Presentation
        # Select the cells back to image & zoom presentation & split & freeze_panes
        sheet.set_selection('A6')
        sheet.set_zoom(80)
        # sheet.split_panes(60,0,5,0)
