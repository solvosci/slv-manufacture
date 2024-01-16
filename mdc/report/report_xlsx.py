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
        #region
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
        f_date = workbook.add_format({'num_format': 'yyyy-mm-dd'})
        f_footer = workbook.add_format(f_cells["footer"])
        f_footer_perc = workbook.add_format(f_cells["footer_perc"])
        f_footer_int = workbook.add_format(f_cells["footer_int"])
        #endregion

        # Set columns widths
        sheet.set_column('A:U', 13)
        sheet.set_column('G:G', 40)  # Workstation name
        sheet.set_column('I:I', 16)  # Client name
        sheet.set_column('U:U', 40)  # Observations = lot_descrip

        # write logo
        logo_file_name = False
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
        sheet.write('A' + header_row_str, _("Start Date"), f_header)
        sheet.write('B' + header_row_str, _("Lot name"), f_header)  # - 1
        sheet.write('C' + header_row_str, _("Product"), f_header)
        sheet.write('D' + header_row_str, _("Shift Code"), f_header)
        sheet.write('E' + header_row_str, _("Line Code"), f_header)
        sheet.write('F' + header_row_str, _("Stage Name"), f_header)
        sheet.write('G' + header_row_str, _("Workstation"), f_header)  # - 6
        sheet.write('H' + header_row_str, _("Employee Code"), f_header)
        sheet.write('I' + header_row_str, _("Employee  Name"), f_header)
        sheet.write('J' + header_row_str, _("Gross Weight"), f_header)
        sheet.write('K' + header_row_str, _("Backs"), f_header)
        sheet.write('L' + header_row_str, _("Crumbs"), f_header)  # - 11
        sheet.write('M' + header_row_str, _("Pieces"), f_header)
        sheet.write('N' + header_row_str, _("Quality"), f_header)
        sheet.write('O' + header_row_str, _("% Backs"), f_header)
        sheet.write('P' + header_row_str, _("% Crumbs"), f_header)
        sheet.write('Q' + header_row_str, _("% Pieces"), f_header)  # - 16
        sheet.write('R' + header_row_str, _("% Total Yield"), f_header)
        sheet.write('S' + header_row_str, _("Speed (MIN/KG)"), f_header)
        sheet.write('T' + header_row_str, _("Time (H)"), f_header)
        sheet.write('U' + header_row_str, _("Observations"), f_header) # - 20
        # -------------------------------------------------------

        # TODO alternate dict list with almost grouped data (still problems with product and date)

        # write data rows
        row = header_row
        wlot_name = ''
        product_name = ''
        wshift_code = ''
        wline_code = ''
        wstage_name = ''
        wemployee_code = ''
        wworkstation_name = ''
        wgross_weight = 0
        wproduct_weight = 0
        wsp1_weight = 0
        wsp2_weight = 0
        wquality = 0
        wtotquality = 0
        wtotal_hours = 0
        wnumreg = 0
        # Filters ---------
        wstart_date = False
        wend_date = False
        wlot_filter = ''
        wgross_frozen = 0
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
            wgross_frozen += obj.gross_weight
            # ------------------------------------------------

            # shift Filter
            if wshift_filter != obj.shift_code:
                wshift_filter_uniq = False

            if (wlot_name != obj.lot_name) or \
            (wemployee_code != obj.employee_code) or \
            (wworkstation_name != obj.workstation_name) or \
            (product_name != obj.product_id.name_get()[0][1]) or \
            (wshift_code != obj.shift_code) or \
            (wline_code != obj.line_code) or \
            (wstage_name != obj.stage_name):
                # lot Filter
                if wlot_filter != obj.lot_name:
                    wlot_filter_uniq = False

                row = row + 1

                # direct data from view database
                sheet.write(row, 0, obj.create_date, f_date)
                sheet.write(row, 1, obj.lot_name, f_data)
                sheet.write(row, 2, obj.product_id.name, f_data)
                sheet.write(row, 3, obj.shift_code, f_data)
                sheet.write(row, 4, obj.line_code, f_data)
                sheet.write(row, 5, obj.stage_name, f_data)
                sheet.write(row, 6, obj.workstation_name, f_data)
                sheet.write(row, 7, obj.employee_code, f_data)
                sheet.write(row, 8, obj.employee_name, f_data)

                # formulation columns
                sheet.write_formula(row, 14,        # - % Backs
                    '=IF(J' + str(row + 1) + '= 0, 0, K' + str(row + 1) + '/J' + str(row + 1) + ')',
                f_percent)
                sheet.write_formula(row, 15,        # - % Crumbs
                    '=IF(J' + str(row + 1) + '= 0, 0, L' + str(row + 1) + '/J' + str(row + 1) + ')',
                f_percent)
                sheet.write_formula(row, 16,        # - % Pieces
                    '=IF(J' + str(row + 1) + '= 0, 0, M' + str(row + 1) + '/J' + str(row + 1) + ')',
                f_percent)
                sheet.write_formula(row, 17,        # - % Total Yield
                    '=IF(J' + str(row + 1) + '= 0, 0, (K' + str(row + 1) + '+L' + str(row + 1) + '+M' + str(row + 1) + ')/J' + str(row + 1) + ')',
                f_percent)  
                sheet.write_formula(row, 18,        # - Speed
                    '=IF(J' + str(row + 1) + '= 0, 0, (T' + str(row + 1) + ' * 60)/J' + str(row + 1) + ')',
                f_data2d)

                wgross_weight = 0
                wproduct_weight = 0
                wsp1_weight = 0
                wsp2_weight = 0
                wtotquality = 0
                wtotal_hours = 0
                wnumreg = 0

            # grouped data vars
            wgross_weight += obj.gross_weight
            wproduct_weight += obj.product_weight
            wshift_code = obj.shift_code
            wline_code = obj.line_code
            wstage_name = obj.stage_name
            wsp1_weight += obj.sp1_weight
            wsp2_weight += obj.sp2_weight
            wtotquality += obj.quality_weight * obj.product_weight
            wtotal_hours += obj.total_hours
            wnumreg += 1

            if wproduct_weight == 0:
                wquality = 0
            else:
                wquality = wtotquality / wproduct_weight

            # columns with grouped data
            sheet.write(row, 9, wgross_weight, f_data2d)
            sheet.write(row, 10, wproduct_weight, f_data2d)
            sheet.write(row, 11, wsp1_weight, f_data2d)
            sheet.write(row, 12, wsp2_weight, f_data2d)
            sheet.write(row, 13, wquality, f_data2d)
            sheet.write(row, 19, wtotal_hours, f_data)

            wlot_name = obj.lot_name
            wemployee_code = obj.employee_code
            wworkstation_name = obj.workstation_name


            # Final Footer Row ------------------------------------------
            for numcol in range(0, 21):
                sheet.write(row + 1, numcol, '', f_footer)
            sheet.write_formula(
                row + 1, 9, '=SUM(J' + str(header_row + 1) + ':J' + str(row + 1) + ')',
            f_footer)
            sheet.write_formula(
                row + 1, 10, '=SUM(K' + str(header_row + 1) + ':K' + str(row + 1) + ')',
            f_footer)
            sheet.write_formula(
                row + 1, 11, '=SUM(L' + str(header_row + 1) + ':L' + str(row + 1) + ')',
            f_footer)
            sheet.write_formula(
                row + 1, 12, '=SUM(M' + str(header_row + 1) + ':M' + str(row + 1) + ')',
            f_footer)
            sheet.write_formula(
                row + 1, 13,
                '=SUMPRODUCT(N' + str(header_row + 1) + ':N' + str(row + 1) + ', '
                'K' + str(header_row + 1) + ':K' + str(row + 1) + ') / K' + str(row + 2),
                f_footer
            )
            sheet.write_formula(                                # - % Backs
                row + 1, 14,
                '=IF(J' + str(row + 2) + '= 0, 0, K' + str(row + 2) + '/J' + str(row + 2) + ')',
            f_footer_perc)
            sheet.write_formula(
                row + 1, 15,
                '=IF(J' + str(row + 2) + '= 0, 0, L' + str(row + 2) + '/J' + str(row + 2) + ')',
            f_footer_perc)
            sheet.write_formula(
                row + 1, 16,
                '=IF(J' + str(row + 2) + '= 0, 0, M' + str(row + 2) + '/J' + str(row + 2) + ')',
            f_footer_perc)
            sheet.write_formula(                                # - % Total Yield
                row + 1, 17,
                '=IF(J' + str(row + 2) + '= 0, 0, (K' + str(row + 2) + '+L' + str(row + 2) + '+M' + str(row + 2) + ')/J' + str(row + 2) + ')',
            f_footer_perc)
            sheet.write_formula(                                # - Speed
                row + 1, 18,  '=IF(J' + str(row + 2) + '= 0, 0, (T' + str(row + 2) + ' * 60)/J' + str(row + 2) + ')',
            f_footer)
            sheet.write_formula(                                # - Total Hours
                row + 1, 19, '=SUM(T' + str(header_row + 1) + ':T' + str(row + 1) + ')',
            f_footer_int)

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
        f_date = workbook.add_format({'num_format': 'yyyy-mm-dd'})
        f_footer = workbook.add_format(f_cells["footer"])
        f_footer_perc = workbook.add_format(f_cells["footer_perc"])
        f_footer_int = workbook.add_format(f_cells["footer_int"])

        # Set columns widths
        sheet.set_column('A:O', 13)
        sheet.set_column('O:O', 40)  # Observations = lot_descrip

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
        sheet.write('A' + header_row_str, _("Start Date"), f_header)    # - 0
        sheet.write('B' + header_row_str, _("Lot name"), f_header)
        sheet.write('C' + header_row_str, _("Product"), f_header)
        sheet.write('D' + header_row_str, _("Shift Code"), f_header)
        sheet.write('E' + header_row_str, _("Line Code"), f_header)
        sheet.write('F' + header_row_str, _("Gross Weight"), f_header)  # - 5
        sheet.write('G' + header_row_str, _("Backs"), f_header)
        sheet.write('H' + header_row_str, _("Crumbs"), f_header)
        sheet.write('I' + header_row_str, _("Pieces"), f_header)
        sheet.write('J' + header_row_str, _("Quality"), f_header)
        sheet.write('K' + header_row_str, _("% Backs"), f_header)   # - 10
        sheet.write('L' + header_row_str, _("% Crumbs"), f_header)
        sheet.write('M' + header_row_str, _("% Pieces"), f_header)
        sheet.write('N' + header_row_str, _("Time (H)"), f_header)
        sheet.write('O' + header_row_str, _("Observations"), f_header)  # - 14
        # -------------------------------------------------------


        # write data rows
        row = header_row
        wlot_name = ''
        product_name = ''
        wshift_code = ''
        wline_code = ''
        wstage_name = ''
        wemployee_code = ''
        wworkstation_name = ''
        wgross_weight = 0
        wproduct_weight = 0
        wsp1_weight = 0
        wsp2_weight = 0
        wquality = 0
        wtotquality = 0
        wtotal_hours = 0
        wnumreg = 0
        # Filters ---------
        wstart_date = False
        wend_date = False
        wlot_filter = ''
        wgross_frozen = 0
        wshift_filter = ''
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
            if wshift_filter == '':
                wshift_filter = obj.shift_code
            wgross_frozen += obj.final_gross_weight
            # ------------------------------------------------

            # shift Filter
            if wshift_filter != obj.shift_code:
                wshift_filter_uniq = False

            if (wlot_name != obj.lot_name) or \
            (product_name != obj.product_id.name_get()[0][1]) or \
            (wshift_code != obj.shift_code) or \
            (wline_code != obj.line_code):

                # lot Filter
                if wlot_filter != obj.lot_name:
                    wlot_filter_uniq = False

                row = row + 1

                # direct data from view database
                sheet.write(row, 0, obj.create_date, f_date)
                sheet.write(row, 1, obj.lot_name, f_data)
                sheet.write(row, 2, obj.product_id.name, f_data)
                sheet.write(row, 3, obj.shift_code, f_data)
                sheet.write(row, 4, obj.line_code, f_data)

                # formulation columns
                sheet.write_formula(row, 10,         # - % Backs
                    '=IF(F' + str(row + 1) + '= 0, 0, G' + str(row + 1) + '/F' + str(row + 1) + ')',
                f_percent)
                sheet.write_formula(row, 11,        # - % Crumbs
                    '=IF(F' + str(row + 1) + '= 0, 0, H' + str(row + 1) + '/F' + str(row + 1) + ')',
                f_percent)
                sheet.write_formula(row, 12,        # - % Pieces
                    '=IF(F' + str(row + 1) + '= 0, 0, I' + str(row + 1) + '/F' + str(row + 1) + ')',
                f_percent)

                wgross_weight = 0
                wproduct_weight = 0
                wsp1_weight = 0
                wsp2_weight = 0
                wtotquality = 0
                wtotal_hours = 0
                wnumreg = 0

            # grouped data vars
            wgross_weight += obj.final_gross_weight
            wproduct_weight += obj.product_weight
            wshift_code = obj.shift_code
            wline_code = obj.line_code
            wsp1_weight += obj.sp1_weight
            wsp2_weight += obj.sp2_weight
            wtotquality += obj.quality_weight * obj.product_weight
            wtotal_hours += obj.total_hours
            wnumreg += 1

            if wproduct_weight == 0:
                wquality = 0
            else:
                wquality = wtotquality / wproduct_weight


            # columns with grouped data
            sheet.write(row, 5, wgross_weight, f_data2d)
            sheet.write(row, 6, wproduct_weight, f_data2d)
            sheet.write(row, 7, wsp1_weight, f_data2d)
            sheet.write(row, 8, wsp2_weight, f_data2d)
            sheet.write(row, 9, wquality, f_data2d)
            sheet.write(row, 13, wtotal_hours, f_data)

            wlot_name = obj.lot_name

            # Final Footer Row ------------------------------------------
            for numcol in range(0, 15):
                sheet.write(row + 1, numcol, '', f_footer)
            sheet.write_formula(
                row + 1, 5, '=SUM(F' + str(header_row + 1) + ':F' + str(row + 1) + ')',
            f_footer)
            sheet.write_formula(
                row + 1, 6, '=SUM(G' + str(header_row + 1) + ':G' + str(row + 1) + ')',
            f_footer)
            sheet.write_formula(
                row + 1, 7, '=SUM(H' + str(header_row + 1) + ':H' + str(row + 1) + ')',
            f_footer)
            sheet.write_formula(
                row + 1, 8, '=SUM(I' + str(header_row + 1) + ':I' + str(row + 1) + ')',
            f_footer)
            sheet.write_formula(
                row + 1, 9,
                '=SUMPRODUCT(J' + str(header_row + 1) + ':J' + str(row + 1) + ', '
                'F' + str(header_row + 1) + ':F' + str(row + 1) + ') / F' + str(row + 2),
                f_footer
            )
            sheet.write_formula(                                # - % Backs
                row + 1, 10,
                '=IF(F' + str(row + 2) + '= 0, 0, G' + str(row + 2) + '/F' + str(row + 2) + ')',
            f_footer_perc)
            sheet.write_formula(                                # - % Crumbs
                row + 1, 11,
                '=IF(F' + str(row + 2) + '= 0, 0, H' + str(row + 2) + '/F' + str(row + 2) + ')',
            f_footer_perc)
            sheet.write_formula(                                # - % Pieces
                row + 1, 12,
                '=IF(F' + str(row + 2) + '= 0, 0, I' + str(row + 2) + '/F' + str(row + 2) + ')',
            f_footer_perc)
            sheet.write_formula(                                # - % Total hours
                row + 1, 13, '=SUM(N' + str(header_row + 1) + ':N' + str(row + 1) + ')',
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
        f_date = workbook.add_format({'num_format': 'yyyy-mm-dd'})
        f_footer = workbook.add_format(f_cells["footer"])
        f_footer_perc = workbook.add_format(f_cells["footer_perc"])
        f_footer_int = workbook.add_format(f_cells["footer_int"])

        # Set columns widths
        sheet.set_column('A:N', 13)
        sheet.set_column('C:C', 40)  # Employee Name
        sheet.set_column('N:N', 40)  # Observations = lot_descrip

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
        sheet.write('A' + header_row_str, _("Start Date"), f_header)
        sheet.write('B' + header_row_str, _("Employee Code"), f_header)
        sheet.write('C' + header_row_str, _("Employee Name"), f_header)
        sheet.write('D' + header_row_str, _("Shift Code"), f_header)
        sheet.write('E' + header_row_str, _("Line Code"), f_header)
        sheet.write('F' + header_row_str, _("Stage Name"), f_header)
        sheet.write('G' + header_row_str, _("Product"), f_header)
        sheet.write('H' + header_row_str, _("Gross Weight"), f_header)
        sheet.write('I' + header_row_str, _("Backs"), f_header)
        sheet.write('J' + header_row_str, _("Crumbs"), f_header)  # - 10
        sheet.write('K' + header_row_str, _("Pieces"), f_header)
        sheet.write('L' + header_row_str, _("Quality"), f_header)
        sheet.write('M' + header_row_str, _("Time (H)"), f_header)        
        sheet.write('N' + header_row_str, _("Observations"), f_header)
        # -------------------------------------------------------

        # TODO alternate dict list with almost grouped data (still problems with product and date)

        # write data rows
        row = header_row
        product_name = ''
        wshift_code = ''
        wline_code = ''
        wstage_name = ''
        wemployee_code = ''
        wworkstation_name = ''
        wgross_weight = 0
        wproduct_weight = 0
        wsp1_weight = 0
        wsp2_weight = 0
        wquality = 0
        wtotquality = 0
        wtotal_hours = 0
        wnumreg = 0
        # Filters ---------
        wstart_date = False
        wend_date = False
        wlot_filter = ''
        wgross_frozen = 0
        wshift_filter = ''
        # -----------------

        for obj in rpt_employee_yield:

            # Filters: ----------------------------------------
            # min a max date
            if wstart_date is False or wstart_date > obj.create_date:
                wstart_date = obj.create_date
            if wend_date is False or wend_date < obj.create_date:
                wend_date = obj.create_date
            # product_name
            product_name = obj.product_id.name_get()[0][1]
            # shift
            if wshift_filter == '':
                wshift_filter = obj.shift_code
            wgross_frozen += obj.gross_weight
            # ------------------------------------------------

            # shift Filter
            if wshift_filter != obj.shift_code:
                wshift_filter_uniq = False

            if (wemployee_code != obj.employee_code) or \
            (product_name != obj.product_id.name_get()[0][1]) or \
            (wshift_code != obj.shift_code) or \
            (wline_code != obj.line_code) or \
            (wstage_name != obj.stage_name):

                row = row + 1

                # direct data from view database
                sheet.write(row, 0, obj.create_date, f_date)
                sheet.write(row, 1, obj.employee_code, f_data)
                sheet.write(row, 2, obj.employee_name, f_data)
                sheet.write(row, 3, obj.shift_code, f_data)
                sheet.write(row, 4, obj.line_code, f_dataL)
                sheet.write(row, 5, obj.stage_name, f_dataL)
                sheet.write(row, 6, obj.product_id.name, f_data2d)

                wgross_weight = 0
                wproduct_weight = 0
                wsp1_weight = 0
                wsp2_weight = 0
                wtotquality = 0
                wtotal_hours = 0
                wnumreg = 0

            # grouped data vars
            wgross_weight += obj.gross_weight
            wproduct_weight += obj.product_weight
            wshift_code = obj.shift_code
            wline_code = obj.line_code
            wstage_name = obj.stage_name
            wsp1_weight += obj.sp1_weight
            wsp2_weight += obj.sp2_weight
            wtotquality += obj.quality_weight * obj.product_weight
            wtotal_hours += obj.total_hours
            wnumreg += 1

            if wproduct_weight == 0:
                wquality = 0
            else:
                wquality = wtotquality / wproduct_weight

            # columns with grouped data
            sheet.write(row, 7, wgross_weight, f_data2d)
            sheet.write(row, 8, wproduct_weight, f_data2d)
            sheet.write(row, 9, wsp1_weight, f_data2d)
            sheet.write(row, 10, wsp2_weight, f_data2d)
            sheet.write(row, 11, wquality, f_data2d)
            sheet.write(row, 12, wtotal_hours, f_data)

            wemployee_code = obj.employee_code


            # Final Footer Row ------------------------------------------
            for numcol in range(0, 14):
                sheet.write(row + 1, numcol, '', f_footer)
            sheet.write_formula(            # - Gross Weight
                row + 1, 7, '=SUM(H' + str(header_row + 1) + ':H' + str(row + 1) + ')',
            f_footer)
            sheet.write_formula(            # - Backs
                row + 1, 8, '=SUM(I' + str(header_row + 1) + ':I' + str(row + 1) + ')',
            f_footer)
            sheet.write_formula(            # - Crumbs
                row + 1, 9, '=SUM(J' + str(header_row + 1) + ':J' + str(row + 1) + ')',
            f_footer)
            sheet.write_formula(            # - Pieces
                row + 1, 10, '=SUM(K' + str(header_row + 1) + ':K' + str(row + 1) + ')',
            f_footer)
            sheet.write_formula(            # - Quality
                row + 1, 11,
                '=IF(H' + str(row + 2) + '= 0, 0, SUMPRODUCT(L' + str(header_row + 1) + ':L' + str(row + 1) + ', H' + str(header_row + 1) + ':H' + str(row + 1) + ')/H' + str(row + 2) + ')',
            f_footer)
            sheet.write_formula(
                row + 1, 12, '=SUM(M' + str(header_row + 1) + ':M' + str(row + 1) + ')',
            f_footer_int)

            # Write Filter -----------------------------------------------
            sheet.write(2, 2, datetime.datetime.now(), f_filter)

        # Final Presentation
        # Select the cells back to image & zoom presentation & split & freeze_panes
        sheet.set_selection('A6')
        sheet.set_zoom(80)
        # sheet.split_panes(60,0,5,0)
