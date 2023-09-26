# -*- coding: utf-8 -*-
from addons.product.models.product_attribute import ProductAttributevalue
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



class ReportRptTracingXlsx(models.AbstractModel):
    _name = 'report.mdc.rpt_tracing'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, rpt_tracing):
        report_name = "rpt_tracing"
        sheet = workbook.add_worksheet("Tracing Report")

        # retrieve rpt_hide_shift_change_data parameter
        hide_shift_data = self.env['ir.config_parameter'].sudo().get_param(
            'mdc.rpt_hide_shift_change_data')

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
        sheet.set_column('A:AJ', 13)
        sheet.set_column('C:C', 40)  # Employee name
        sheet.set_column('K:K', 16)  # Client name
        sheet.set_column('AK:AK', 40)  # Observations = lot_descrip
        if hide_shift_data:
            sheet.set_column('R:T', 0, None, {'hidden': 1})

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
        sheet.write(1, 2, _("TRACING REPORT"), f_title)

        # write Filter
        sheet.write(2, 2, _("Date From:"), f_filter)

        header_row = 5
        header_row_str = str(header_row + 1)
        # write column header ----------------------------------------
        sheet.write('A' + header_row_str, _("Workstation"), f_header)  # - 0
        sheet.write('B' + header_row_str, _("Employee Code"), f_header)
        sheet.write('C' + header_row_str, _("Employee Name"), f_header)
        sheet.write('D' + header_row_str, _("Contract"), f_header)
        sheet.write('E' + header_row_str, _("Employee Incorporation date"), f_header)
        sheet.write('F' + header_row_str, _("Manufacturing date"), f_header)  # - 5
        sheet.write('G' + header_row_str, _("Employee seniority"), f_header)
        sheet.write('H' + header_row_str, _("MO"), f_header)
        sheet.write('I' + header_row_str, _("Product"), f_header)
        sheet.write('J' + header_row_str, _("Cleaning"), f_header)
        sheet.write('K' + header_row_str, _("Client"), f_header)  # - 10
        sheet.write('L' + header_row_str, _("Gross Reference"), f_header)
        sheet.write('M' + header_row_str, _("Cooking yield"), f_header)
        sheet.write('N' + header_row_str, _("Cooking yield Std"), f_header)
        sheet.write('O' + header_row_str, _("Gross"), f_header)
        sheet.write('P' + header_row_str, _("Backs"), f_header)  # - 15
        sheet.write('Q' + header_row_str, _("Crumbs"), f_header)
        sheet.write('R' + header_row_str, _("Shift Change Gross"), f_header)
        sheet.write('S' + header_row_str, _("Shift Change Backs"), f_header)
        sheet.write('T' + header_row_str, _("Shift Change Crumbs"), f_header)
        sheet.write('U' + header_row_str, _("Quality"), f_header)  # - 20
        sheet.write('V' + header_row_str, _("Time"), f_header)
        sheet.write('W' + header_row_str, _("% Backs"), f_header)
        sheet.write('X' + header_row_str, _("STD Back"), f_header)
        sheet.write('Y' + header_row_str, _("% Crumbs"), f_header)
        sheet.write('Z' + header_row_str, _("% Total Yield"), f_header)  # - 25
        sheet.write('AA' + header_row_str, _("STD Crumbs"), f_header)
        sheet.write('AB' + header_row_str, _("MO."), f_header)
        sheet.write('AC' + header_row_str, _("STD MO"), f_header)
        sheet.write('AD' + header_row_str, _("IND Backs"), f_header_ind)
        sheet.write('AE' + header_row_str, _("IND MO"), f_header_ind)  # - 30
        sheet.write('AF' + header_row_str, _("IND Crumbs"), f_header_ind)
        sheet.write('AG' + header_row_str, _("IND Quality"), f_header_ind)
        sheet.write('AH' + header_row_str, _("IND Cleaning"), f_header_ind)
        sheet.write('AI' + header_row_str, _("Box Backs"), f_header)
        sheet.write('AJ' + header_row_str, _("Box Crumbs"), f_header)  # - 35
        sheet.write('AK' + header_row_str, _("Observations"), f_header)
        # -------------------------------------------------------

        # TODO alternate dict list with almost grouped data (still problems with product and date)

        # write data rows
        row = header_row
        wlot_name = ''
        product_name = ''
        wemployee_code = ''
        wworkstation_name = ''
        wgross_weight_reference = 0
        wgross_weight = 0
        wproduct_weight = 0
        wsp1_weight = 0
        wshared_gross_weight_reference = 0
        wshared_gross_weight = 0
        wshared_product_weight = 0
        wshared_sp1_weight = 0
        wproduct_boxes = 0
        wsp1_boxes = 0
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
        wlot_filter_uniq = True
        wshift_filter_uniq = True
        # -----------------

        for obj in rpt_tracing:

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
            wgross_frozen += obj.gross_weight_reference
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
                sheet.write(row, 0, obj.workstation_name, f_data)
                sheet.write(row, 1, obj.employee_code, f_data)
                sheet.write(row, 2, obj.employee_name, f_data)
                sheet.write(row, 3, obj.contract_name, f_data)
                wemployee_date_start = ''
                if obj.employee_date_start:
                    wemployee_date_start = tools.format_date(self.env, obj.employee_date_start)
                sheet.write(row, 4, wemployee_date_start, f_data)
                formatted_date = tools.format_date(self.env, obj.create_date)
                sheet.write(row, 5, formatted_date, f_data)
                sheet.write(row, 7, obj.lot_name, f_data)
                sheet.write(row, 8, obj.product_id.name, f_dataL)
                variable_attributes = obj.product_id.attribute_line_ids.mapped('attribute_id')
                variant = obj.product_id.attribute_value_ids._variant_name(variable_attributes)
                sheet.write(row, 9, variant, f_dataL)
                sheet.write(row, 10, obj.client_name, f_dataL)
                wlot_descrip = ''
                if obj.lot_descrip:
                    wlot_descrip = obj.lot_descrip
                sheet.write(row, 36, wlot_descrip, f_dataL)

                # std columns
                wcooking_yield = ''
                if obj.lot_finished:
                    wcooking_yield = obj.coef_weight_lot
                sheet.write(row, 12, wcooking_yield, f_data2d)
                sheet.write(row, 13, (100 - obj.std_loss) / 100, f_percent)
                sheet.write(row, 23, obj.std_yield_product, f_data2d)
                sheet.write(row, 26, obj.std_yield_sp1, f_data2d)
                sheet.write(row, 28, obj.std_speed, f_data2d)

                # formulation columns
                sheet.write_formula(row, 6,
                                    '=IF(E' + str(row + 1) + '= "", "", F' + str(row + 1) + '-E' + str(row + 1) + ')',
                                    f_data)  # - Employee seniority
                sheet.write_formula(row, 22,
                                    '=IF(L' + str(row + 1) + '= 0, 0, P' + str(row + 1) + '/L' + str(row + 1) + ')',
                                    f_percent)  # - % Backs
                sheet.write_formula(row, 24,
                                    '=IF(L' + str(row + 1) + '= 0, 0, Q' + str(row + 1) + '/L' + str(row + 1) + ')',
                                    f_percent)  # - % Crumbs
                sheet.write_formula(row, 25, '=IF(L' + str(row + 1) + '= 0, 0, (P' + str(row + 1) + '+Q' + str(
                    row + 1) + ')/L' + str(row + 1) + ')', f_percent)  # - % Total Yield
                sheet.write_formula(row, 27, '=IF(L' + str(row + 1) + '= 0, 0, (V' + str(row + 1) + ' * 60)/L' + str(
                    row + 1) + ')', f_data2d)  # - MO

                # Ind columns
                sheet.write_formula(row, 29, '=IF(X' + str(row + 1) + '= 0, 0, (W' + str(row + 1) + '/X' + str(
                    row + 1) + '/1.15) * 100)', f_percent)  # - IND Backs
                sheet.write_formula(row, 30, '=IF(AB' + str(row + 1) + '= 0, 0, (AC' + str(row + 1) + '/AB' + str(
                    row + 1) + '/1.15))', f_percent)  # - IND MO
                sheet.write_formula(row, 31, '=IF(AA' + str(row + 1) + '= 0, 0, (Y' + str(row + 1) + '/AA' + str(
                    row + 1) + '/1.15) * 100)', f_percent)  # - IND Crumbs
                sheet.write_formula(row, 32, '=U' + str(row + 1) + '/100', f_percent)  # - IND Quality
                sheet.write_formula(row, 33,
                                    '0.6 * AD' + str(row + 1) + ' + 0.3 * AE' + str(row + 1) + ' + 0.1 * AG' + str(
                                        row + 1), f_percent)  # - IND Cleaning

                wgross_weight_reference = 0
                wgross_weight = 0
                wproduct_weight = 0
                wsp1_weight = 0
                wshared_gross_weight_reference = 0
                wshared_gross_weight = 0
                wshared_product_weight = 0
                wshared_sp1_weight = 0
                wproduct_boxes = 0
                wsp1_boxes = 0
                wtotquality = 0
                wtotal_hours = 0
                wnumreg = 0

            # grouped data vars
            wgross_weight_reference += obj.gross_weight_reference
            wgross_weight += obj.gross_weight
            wproduct_weight += obj.product_weight
            wsp1_weight += obj.sp1_weight
            wshared_gross_weight_reference += obj.shared_gross_weight_reference
            wshared_gross_weight += obj.shared_gross_weight
            wshared_product_weight += obj.shared_product_weight
            wshared_sp1_weight += obj.shared_sp1_weight
            wproduct_boxes += obj.product_boxes
            wsp1_boxes += obj.sp1_boxes
            wtotquality += obj.quality * (obj.product_weight + obj.shared_product_weight / 2)
            wtotal_hours += obj.total_hours
            wnumreg += 1

            if (wproduct_weight + wshared_product_weight / 2) == 0:
                wquality = 0
            else:
                wquality = wtotquality / (wproduct_weight + wshared_product_weight / 2)

            # columns with grouped data
            sheet.write(row, 11, wgross_weight_reference, f_data2d)
            sheet.write(row, 14, wgross_weight, f_data2d)
            sheet.write(row, 15, wproduct_weight, f_data2d)
            sheet.write(row, 16, wsp1_weight, f_data2d)
            sheet.write(row, 17, wshared_gross_weight_reference, f_data2d)
            sheet.write(row, 18, wshared_product_weight, f_data2d)
            sheet.write(row, 19, wshared_sp1_weight, f_data2d)
            sheet.write(row, 20, wquality, f_data2d)
            sheet.write(row, 21, wtotal_hours, f_data2d)
            sheet.write(row, 34, wproduct_boxes, f_data)
            sheet.write(row, 35, wsp1_boxes, f_data)

            wlot_name = obj.lot_name
            wemployee_code = obj.employee_code
            wworkstation_name = obj.workstation_name

            # Final Footer Row ------------------------------------------
            for numcol in range(0, 37):
                sheet.write(row + 1, numcol, '', f_footer)
            sheet.write_formula(row + 1, 11, '=SUM(L' + str(header_row + 1) + ':L' + str(row + 1) + ')', f_footer)
            sheet.write_formula(row + 1, 12, '=M' + str(row + 1), f_footer)
            sheet.write_formula(row + 1, 13, '=N' + str(row + 1), f_footer_perc)
            sheet.write_formula(row + 1, 14, '=SUM(O' + str(header_row + 1) + ':O' + str(row + 1) + ')', f_footer)
            sheet.write_formula(row + 1, 15, '=SUM(P' + str(header_row + 1) + ':P' + str(row + 1) + ')', f_footer)
            sheet.write_formula(row + 1, 16, '=SUM(Q' + str(header_row + 1) + ':Q' + str(row + 1) + ')', f_footer)
            sheet.write_formula(row + 1, 17, '=SUM(R' + str(header_row + 1) + ':R' + str(row + 1) + ')', f_footer)
            sheet.write_formula(row + 1, 18, '=SUM(S' + str(header_row + 1) + ':S' + str(row + 1) + ')', f_footer)
            sheet.write_formula(row + 1, 19, '=SUM(T' + str(header_row + 1) + ':T' + str(row + 1) + ')', f_footer)
            sheet.write_formula(row + 1, 21, '=SUM(V' + str(header_row + 1) + ':V' + str(row + 1) + ')', f_footer)
            sheet.write_formula(row + 1, 23, '=AVERAGE(X' + str(header_row + 1) + ':X' + str(row + 1) + ')', f_footer)
            sheet.write_formula(row + 1, 26, '=AVERAGE(AA' + str(header_row + 1) + ':AA' + str(row + 1) + ')', f_footer)
            sheet.write_formula(row + 1, 28, '=AVERAGE(AC' + str(header_row + 1) + ':AC' + str(row + 1) + ')', f_footer)
            # formulation columns
            sheet.write_formula(row + 1, 20,
                                '=IF(L' + str(row + 2) + '= 0, 0 , SUMPRODUCT(U' + str(header_row + 1) + ':U' + str(
                                    row + 1) + ', L' + str(header_row + 1) + ':L' + str(row + 1) + ') / L' + str(
                                    row + 2) + ')', f_footer)
            sheet.write_formula(row + 1, 22,
                                '=IF(L' + str(row + 2) + '= 0, 0, P' + str(row + 2) + '/L' + str(row + 2) + ')',
                                f_footer_perc)  # - % Backs
            sheet.write_formula(row + 1, 24,
                                '=IF(L' + str(row + 2) + '= 0, 0, Q' + str(row + 2) + '/L' + str(row + 2) + ')',
                                f_footer_perc)  # - % Crumbs
            sheet.write_formula(row + 1, 25, '=IF(L' + str(row + 2) + '= 0, 0, (P' + str(row + 2) + '+Q' + str(
                row + 2) + ')/L' + str(row + 2) + ')', f_footer_perc)  # - % Total Yield
            sheet.write_formula(row + 1, 27,
                                '=IF(L' + str(row + 2) + '= 0, 0, (V' + str(row + 2) + ' * 60)/L' + str(row + 2) + ')',
                                f_footer)  # - MO
            # Ind columns
            sheet.write_formula(row + 1, 29, '=IF(X' + str(row + 2) + '= 0, 0, (W' + str(row + 2) + '/X' + str(
                row + 2) + '/1.15) * 100)', f_footer_perc)  # - IND Backs
            sheet.write_formula(row + 1, 30, '=IF(AB' + str(row + 2) + '= 0, 0, (AC' + str(row + 2) + '/AB' + str(
                row + 2) + '/1.15))', f_footer_perc)  # - IND MO
            sheet.write_formula(row + 1, 31, '=IF(AA' + str(row + 2) + '= 0, 0, (Y' + str(row + 2) + '/AA' + str(
                row + 2) + '/1.15) * 100)', f_footer_perc)  # - IND Crumbs
            sheet.write_formula(row + 1, 32, '=U' + str(row + 2) + '/100', f_footer_perc)  # - IND Quality
            sheet.write_formula(row + 1, 33,
                                '0.6 * AD' + str(row + 2) + ' + 0.3 * AE' + str(row + 2) + ' + 0.1 * AG' + str(row + 2),
                                f_footer_perc)  # - IND Cleaning

            sheet.write_formula(row + 1, 34, '=SUM(AI' + str(header_row + 1) + ':AI' + str(row + 1) + ')', f_footer_int)
            sheet.write_formula(row + 1, 35, '=SUM(AJ' + str(header_row + 1) + ':AJ' + str(row + 1) + ')', f_footer_int)

            # Write Filter -----------------------------------------------
            sheet.write(2, 2, datetime.datetime.now(), f_filter)
            # datefilter = _("Date From: %s to %s") % (wstart_date, wend_date)
            # if wstart_date == wend_date:
            #    datefilter = _("Date: %s") % wstart_date
            # if wlot_filter_uniq:
            #    datefilter = datefilter + ' // ' + _("Lot: %s") % wlot_filter
            #    datefilter = datefilter + ' // ' + _("%.2f Kg Frozen") % wgross_frozen
            # if wshift_filter_uniq:
            #    datefilter = datefilter + ' // ' + _("Shift: %s") % wshift_filter
            # sheet.write(2, 2, datefilter, f_filter)
            # if wlot_filter_uniq:
            #    sheet.write(3, 2, product_name, f_filter)

        # Final Presentation
        # Select the cells back to image & zoom presentation & split & freeze_panes
        sheet.set_selection('A6')
        sheet.set_zoom(80)
        # sheet.split_panes(60,0,5,0)


class ReportRptManufacturingXlsx(models.AbstractModel):
    _name = 'report.mdc.rpt_manufacturing'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, rpt_manufacturing):
        report_name = "rpt_manufacturing"
        sheet = workbook.add_worksheet("Manufacturing Report")

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
        sheet.set_column('A:AJ', 13)
        sheet.set_column('C:C', 40) # Employee name
        sheet.set_column('K:K', 16)  # Client name
        sheet.set_column('AK:AK', 40)  # Observations = lot_descrip
        if hide_shift_data:
            sheet.set_column('R:T', 0, None, {'hidden': 1})

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
        sheet.write(1, 2, _("MANUFACTURING REPORT"), f_title)

        # write Filter
        sheet.write(2, 2, _("Date From:"), f_filter)

        header_row=5
        header_row_str = str(header_row+1)
        # write column header ----------------------------------------
        sheet.write('A' + header_row_str , _("Workstation"), f_header) # - 0
        sheet.write('B' + header_row_str, _("Employee Code"), f_header)
        sheet.write('C' + header_row_str, _("Employee Name"), f_header)
        sheet.write('D' + header_row_str, _("Contract"), f_header)
        sheet.write('E' + header_row_str, _("Employee Incorporation date"), f_header)
        sheet.write('F' + header_row_str, _("Manufacturing date"), f_header) # - 5
        sheet.write('G' + header_row_str, _("Employee seniority"), f_header)
        sheet.write('H' + header_row_str, _("MO"), f_header)
        sheet.write('I' + header_row_str, _("Product"), f_header)
        sheet.write('J' + header_row_str, _("Cleaning"), f_header)
        sheet.write('K' + header_row_str, _("Client"), f_header) # - 10
        sheet.write('L' + header_row_str, _("Gross Reference"), f_header)
        sheet.write('M' + header_row_str, _("Cooking yield"), f_header)
        sheet.write('N' + header_row_str, _("Cooking yield Std"), f_header)
        sheet.write('O' + header_row_str, _("Gross"), f_header)
        sheet.write('P' + header_row_str, _("Backs"), f_header) # - 15
        sheet.write('Q' + header_row_str, _("Crumbs"), f_header)
        sheet.write('R' + header_row_str, _("Shift Change Gross"), f_header)
        sheet.write('S' + header_row_str, _("Shift Change Backs"), f_header)
        sheet.write('T' + header_row_str, _("Shift Change Crumbs"), f_header)
        sheet.write('U' + header_row_str, _("Quality"), f_header) # - 20
        sheet.write('V' + header_row_str, _("Time"), f_header)
        sheet.write('W' + header_row_str, _("% Backs"), f_header)
        sheet.write('X' + header_row_str, _("STD Back"), f_header)
        sheet.write('Y' + header_row_str, _("% Crumbs"), f_header)
        sheet.write('Z' + header_row_str, _("% Total Yield"), f_header) # - 25
        sheet.write('AA' + header_row_str, _("STD Crumbs"), f_header)
        sheet.write('AB' + header_row_str, _("MO."), f_header)
        sheet.write('AC' + header_row_str, _("STD MO"), f_header)
        sheet.write('AD' + header_row_str, _("IND Backs"), f_header_ind)
        sheet.write('AE' + header_row_str, _("IND MO"), f_header_ind) # - 30
        sheet.write('AF' + header_row_str, _("IND Crumbs"), f_header_ind)
        sheet.write('AG' + header_row_str, _("IND Quality"), f_header_ind)
        sheet.write('AH' + header_row_str, _("IND Cleaning"), f_header_ind)
        sheet.write('AI' + header_row_str, _("Box Backs"), f_header)
        sheet.write('AJ' + header_row_str, _("Box Crumbs"), f_header) # - 35
        sheet.write('AK' + header_row_str, _("Observations"), f_header)
        # -------------------------------------------------------

        # TODO alternate dict list with almost grouped data (still problems with product and date)

        # write data rows
        row=header_row
        wlot_name = ''
        product_name = ''
        wemployee_code = ''
        wworkstation_name = ''
        wgross_weight_reference = 0
        wgross_weight = 0
        wproduct_weight = 0
        wsp1_weight = 0
        wshared_gross_weight_reference = 0
        wshared_gross_weight = 0
        wshared_product_weight = 0
        wshared_sp1_weight = 0
        wproduct_boxes =0
        wsp1_boxes =0
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
        wlot_filter_uniq = True
        wshift_filter_uniq = True
        # -----------------

        for obj in rpt_manufacturing:

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
            wgross_frozen += obj.gross_weight_reference
            # ------------------------------------------------

            # shift Filter
            if wshift_filter != obj.shift_code:
                wshift_filter_uniq = False

            if (wlot_name != obj.lot_name) or (wemployee_code != obj.employee_code) or (wworkstation_name != obj.workstation_name):
                # lot Filter
                if wlot_filter != obj.lot_name:
                    wlot_filter_uniq = False

                row = row + 1

                # direct data from view database
                sheet.write(row, 0, obj.workstation_name, f_data)
                sheet.write(row, 1, obj.employee_code, f_data)
                sheet.write(row, 2, obj.employee_name, f_data)
                sheet.write(row, 3, obj.contract_name, f_data)
                wemployee_date_start=''
                if obj.employee_date_start:
                    wemployee_date_start=tools.format_date(self.env, obj.employee_date_start)
                sheet.write(row, 4, wemployee_date_start, f_data)
                formatted_date = tools.format_date(self.env, obj.create_date)
                sheet.write(row, 5, formatted_date, f_data)
                sheet.write(row, 7, obj.lot_name, f_data)
                sheet.write(row, 8, obj.product_id.name, f_dataL)
                variable_attributes = obj.product_id.attribute_line_ids.mapped('attribute_id')
                variant = obj.product_id.attribute_value_ids._variant_name(variable_attributes)
                sheet.write(row, 9, variant, f_dataL)
                sheet.write(row, 10, obj.client_name, f_dataL)
                wlot_descrip = ''
                if obj.lot_descrip:
                    wlot_descrip = obj.lot_descrip
                sheet.write(row, 36, wlot_descrip, f_dataL)

                # std columns
                wcooking_yield = ''
                if obj.lot_finished:
                    wcooking_yield = obj.coef_weight_lot
                sheet.write(row, 12, wcooking_yield, f_data2d)
                sheet.write(row, 13, (100-obj.std_loss)/100, f_percent)
                sheet.write(row, 23, obj.std_yield_product, f_data2d)
                sheet.write(row, 26, obj.std_yield_sp1, f_data2d)
                sheet.write(row, 28, obj.std_speed, f_data2d)

                # formulation columns
                sheet.write_formula(row, 6, '=IF(E' + str(row + 1) + '= "", "", F' + str(row + 1) + '-E' + str(row + 1) + ')', f_data) # - Employee seniority
                sheet.write_formula(row, 22, '=IF(L' + str(row + 1) + '= 0, 0, P' + str(row + 1) + '/L' + str(row + 1) + ')', f_percent)  # - % Backs
                sheet.write_formula(row, 24, '=IF(L' + str(row + 1) + '= 0, 0, Q' + str(row + 1) + '/L' + str(row + 1) + ')', f_percent)  # - % Crumbs
                sheet.write_formula(row, 25, '=IF(L' + str(row + 1) + '= 0, 0, (P' + str(row + 1) + '+Q' + str(row + 1) + ')/L' + str(row + 1) + ')' ,f_percent)  # - % Total Yield
                sheet.write_formula(row, 27, '=IF(L' + str(row + 1) + '= 0, 0, (V' + str(row + 1) + ' * 60)/L' + str(row + 1) + ')', f_data2d)  # - MO

                # Ind columns
                sheet.write_formula(row, 29, '=IF(X' + str(row + 1) + '= 0, 0, (W' + str(row + 1) + '/X' + str(row + 1) + '/1.15) * 100)', f_percent) # - IND Backs
                sheet.write_formula(row, 30, '=IF(AB' + str(row + 1) + '= 0, 0, (AC' + str(row + 1) + '/AB' + str(row + 1) + '/1.15))', f_percent) # - IND MO
                sheet.write_formula(row, 31, '=IF(AA' + str(row + 1) + '= 0, 0, (Y' + str(row + 1) + '/AA' + str(row + 1) + '/1.15) * 100)', f_percent) # - IND Crumbs
                sheet.write_formula(row, 32, '=U' + str(row + 1) + '/100', f_percent) # - IND Quality
                sheet.write_formula(row, 33, '0.6 * AD' + str(row + 1) + ' + 0.3 * AE' + str(row + 1) + ' + 0.1 * AG' + str(row + 1), f_percent) # - IND Cleaning

                wgross_weight_reference = 0
                wgross_weight = 0
                wproduct_weight = 0
                wsp1_weight = 0
                wshared_gross_weight_reference = 0
                wshared_gross_weight = 0
                wshared_product_weight = 0
                wshared_sp1_weight = 0
                wproduct_boxes = 0
                wsp1_boxes = 0
                wtotquality = 0
                wtotal_hours = 0
                wnumreg = 0

            # grouped data vars
            wgross_weight_reference += obj.gross_weight_reference
            wgross_weight += obj.gross_weight
            wproduct_weight += obj.product_weight
            wsp1_weight += obj.sp1_weight
            wshared_gross_weight_reference += obj.shared_gross_weight_reference
            wshared_gross_weight += obj.shared_gross_weight
            wshared_product_weight += obj.shared_product_weight
            wshared_sp1_weight += obj.shared_sp1_weight
            wproduct_boxes += obj.product_boxes
            wsp1_boxes += obj.sp1_boxes
            wtotquality += obj.quality * (obj.product_weight + obj.shared_product_weight / 2)
            wtotal_hours += obj.total_hours
            wnumreg += 1

            if (wproduct_weight + wshared_product_weight/2) == 0:
                wquality=0
            else:
                wquality = wtotquality/(wproduct_weight + wshared_product_weight/2)

            #columns with grouped data
            sheet.write(row, 11, wgross_weight_reference, f_data2d)
            sheet.write(row, 14, wgross_weight, f_data2d)
            sheet.write(row, 15, wproduct_weight, f_data2d)
            sheet.write(row, 16, wsp1_weight, f_data2d)
            sheet.write(row, 17, wshared_gross_weight_reference, f_data2d)
            sheet.write(row, 18, wshared_product_weight, f_data2d)
            sheet.write(row, 19, wshared_sp1_weight, f_data2d)
            sheet.write(row, 20, wquality, f_data2d)
            sheet.write(row, 21, wtotal_hours, f_data2d)
            sheet.write(row, 34, wproduct_boxes, f_data)
            sheet.write(row, 35, wsp1_boxes, f_data)

            wlot_name = obj.lot_name
            wemployee_code = obj.employee_code
            wworkstation_name = obj.workstation_name

            # Final Footer Row ------------------------------------------
            for numcol in range (0, 37):
                sheet.write(row + 1, numcol, '' ,f_footer)
            sheet.write_formula(row + 1, 11, '=SUM(L' + str(header_row + 1) + ':L' + str(row + 1) + ')', f_footer)
            sheet.write_formula(row + 1, 12, '=M' + str(row + 1), f_footer)
            sheet.write_formula(row + 1, 13, '=N' + str(row + 1), f_footer_perc)
            sheet.write_formula(row + 1, 14, '=SUM(O' + str(header_row + 1) + ':O' + str(row + 1) + ')', f_footer)
            sheet.write_formula(row + 1, 15, '=SUM(P' + str(header_row + 1) + ':P' + str(row + 1) + ')', f_footer)
            sheet.write_formula(row + 1, 16, '=SUM(Q' + str(header_row + 1) + ':Q' + str(row + 1) + ')', f_footer)
            sheet.write_formula(row + 1, 17, '=SUM(R' + str(header_row + 1) + ':R' + str(row + 1) + ')', f_footer)
            sheet.write_formula(row + 1, 18, '=SUM(S' + str(header_row + 1) + ':S' + str(row + 1) + ')', f_footer)
            sheet.write_formula(row + 1, 19, '=SUM(T' + str(header_row + 1) + ':T' + str(row + 1) + ')', f_footer)
            sheet.write_formula(row + 1, 21, '=SUM(V' + str(header_row + 1) + ':V' + str(row + 1) + ')', f_footer)
            sheet.write_formula(row + 1, 23, '=AVERAGE(X' + str(header_row + 1) + ':X' + str(row + 1) + ')', f_footer)
            sheet.write_formula(row + 1, 26, '=AVERAGE(AA' + str(header_row + 1) + ':AA' + str(row + 1) + ')', f_footer)
            sheet.write_formula(row + 1, 28, '=AVERAGE(AC' + str(header_row + 1) + ':AC' + str(row + 1) + ')', f_footer)
                # formulation columns
            sheet.write_formula(row + 1, 20, '=IF(L' + str(row + 2) + '= 0, 0 , SUMPRODUCT(U' + str(header_row + 1) + ':U' + str(row + 1) + ', L' + str(header_row + 1) + ':L' + str(row + 1) + ') / L' + str(row + 2) + ')', f_footer)
            sheet.write_formula(row + 1, 22, '=IF(L' + str(row + 2) + '= 0, 0, P' + str(row + 2) + '/L' + str(row + 2) + ')', f_footer_perc)  # - % Backs
            sheet.write_formula(row + 1, 24, '=IF(L' + str(row + 2) + '= 0, 0, Q' + str(row + 2) + '/L' + str(row + 2) + ')', f_footer_perc)  # - % Crumbs
            sheet.write_formula(row + 1, 25, '=IF(L' + str(row + 2) + '= 0, 0, (P' + str(row + 2) + '+Q' + str(row + 2) + ')/L' + str(row + 2) + ')', f_footer_perc)  # - % Total Yield
            sheet.write_formula(row + 1, 27, '=IF(L' + str(row + 2) + '= 0, 0, (V' + str(row + 2) + ' * 60)/L' + str(row + 2) + ')', f_footer)  # - MO
                # Ind columns
            sheet.write_formula(row + 1, 29, '=IF(X' + str(row + 2) + '= 0, 0, (W' + str(row + 2) + '/X' + str(row + 2) + '/1.15) * 100)', f_footer_perc)  # - IND Backs
            sheet.write_formula(row + 1, 30, '=IF(AB' + str(row + 2) + '= 0, 0, (AC' + str(row + 2) + '/AB' + str(row + 2) + '/1.15))', f_footer_perc)  # - IND MO
            sheet.write_formula(row + 1, 31, '=IF(AA' + str(row + 2) + '= 0, 0, (Y' + str(row + 2) + '/AA' + str(row + 2) + '/1.15) * 100)', f_footer_perc)  # - IND Crumbs
            sheet.write_formula(row + 1, 32, '=U' + str(row + 2) + '/100', f_footer_perc)  # - IND Quality
            sheet.write_formula(row + 1, 33, '0.6 * AD' + str(row + 2) + ' + 0.3 * AE' + str(row + 2) + ' + 0.1 * AG' + str(row + 2), f_footer_perc)  # - IND Cleaning

            sheet.write_formula(row + 1, 34, '=SUM(AI' + str(header_row + 1) + ':AI' + str(row + 1) + ')', f_footer_int)
            sheet.write_formula(row + 1, 35, '=SUM(AJ' + str(header_row + 1) + ':AJ' + str(row + 1) + ')', f_footer_int)

            # Write Filter -----------------------------------------------
            sheet.write(2, 2, datetime.datetime.now(), f_filter)
            #datefilter = _("Date From: %s to %s") % (wstart_date, wend_date)
            # if wstart_date == wend_date:
            #    datefilter = _("Date: %s") % wstart_date
            # if wlot_filter_uniq:
            #    datefilter = datefilter + ' // ' + _("Lot: %s") % wlot_filter
            #    datefilter = datefilter + ' // ' + _("%.2f Kg Frozen") % wgross_frozen
            #if wshift_filter_uniq:
            #    datefilter = datefilter + ' // ' + _("Shift: %s") % wshift_filter
            # sheet.write(2, 2, datefilter, f_filter)
            # if wlot_filter_uniq:
            #    sheet.write(3, 2, product_name, f_filter)

        # Final Presentation
        # Select the cells back to image & zoom presentation & split & freeze_panes
        sheet.set_selection('A6')
        sheet.set_zoom(80)
        # sheet.split_panes(60,0,5,0)


class ReportRptIndicatorsXlsx(models.AbstractModel):
    _name = 'report.mdc.rpt_indicators'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, rpt_indicators):
        report_name = "rpt_indicators"
        sheet = workbook.add_worksheet("Indicators Report")

        # retrieve rpt_hide_shift_change_data parameter
        hide_shift_data = self.env['ir.config_parameter'].sudo().get_param(
            'mdc.rpt_hide_shift_change_data')

        # General sheet style
        sheet.set_landscape()
        sheet.repeat_rows(0, 5)
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
        sheet.set_column('A:U', 13)
        sheet.set_column('B:B', 40)  # Employee name
        if hide_shift_data:
            sheet.set_column('C:C', 0, None, {'hidden': 1})

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
        sheet.write(1, 3, _("INDICATORS REPORT"), f_title)

        # write Filter
        # sheet.write(2, 2, _("Date From:"), f_filter)

        header_row = 5
        header_row_str = str(header_row + 1)
        # write column header ----------------------------------------
        sheet.write('A' + header_row_str, _("Employee Code"), f_header) # - 0
        sheet.write('B' + header_row_str, _("Employee Name"), f_header)
        sheet.write('C' + header_row_str, _("Shift"), f_header)
        sheet.write('D' + header_row_str, _("MO"), f_header)
        sheet.write('E' + header_row_str, _("Manufacturing date"), f_header)
        sheet.write('F' + header_row_str, _("Gross Reference"), f_header) # - 5
        sheet.write('G' + header_row_str, _("Backs"), f_header)
        sheet.write('H' + header_row_str, _("Crumbs"), f_header)
        sheet.write('I' + header_row_str, _("Quality"), f_header)
        sheet.write('J' + header_row_str, _("Time"), f_header)
        sheet.write('K' + header_row_str, _("% Backs"), f_header) # - 10
        sheet.write('L' + header_row_str, _("STD Back"), f_header)
        sheet.write('M' + header_row_str, _("% Crumbs"), f_header)
        sheet.write('N' + header_row_str, _("STD Crumbs"), f_header)
        sheet.write('O' + header_row_str, _("MO."), f_header)
        sheet.write('P' + header_row_str, _("STD MO"), f_header) # - 15
        sheet.write('Q' + header_row_str, _("IND Backs"), f_header_ind)
        sheet.write('R' + header_row_str, _("IND MO"), f_header_ind)
        sheet.write('S' + header_row_str, _("IND Crumbs"), f_header_ind)
        sheet.write('T' + header_row_str, _("IND Quality"), f_header_ind)
        sheet.write('U' + header_row_str, _("IND Cleaning"), f_header_ind) # - 20
        # -------------------------------------------------------

        # TODO alternate dict list with almost grouped data (still problems with product and date)

        # write data rows
        row = header_row
        wlot_name = ''
        product_name = ''
        wemployee_code = ''
        wgross_weight_reference = 0
        wproduct_weight = 0
        wshared_product_weight = 0
        wsp1_weight = 0
        wquality = 0
        wtotquality = 0
        wtotal_hours = 0
        wnumreg = 0

        # Filters ---------
        # -----------------

        for obj in rpt_indicators:

            # Filters: ----------------------------------------
            # min a max date
            # ------------------------------------------------

            # shift Filter

            if (wlot_name != obj.lot_name) or (wemployee_code != obj.employee_code):
                # lot Filter

                row = row + 1

                # direct data from view database
                sheet.write(row, 0, obj.employee_code, f_data)
                sheet.write(row, 1, obj.employee_name, f_data)
                sheet.write(row, 2, obj.shift_code, f_data)
                sheet.write(row, 3, obj.lot_name, f_data)
                formatted_date = tools.format_date(self.env, obj.create_date)
                sheet.write(row, 4, formatted_date, f_data)

                # std columns
                sheet.write(row, 11, obj.std_yield_product, f_data2d)
                sheet.write(row, 13, obj.std_yield_sp1, f_data2d)
                sheet.write(row, 15, obj.std_speed, f_data2d)

                # formulation columns
                sheet.write_formula(row, 10,
                                    '=IF(F' + str(row + 1) + '= 0, 0, G' + str(row + 1) + '/F' + str(row + 1) + ')',
                                    f_percent)  # - % Backs
                sheet.write_formula(row, 12,
                                    '=IF(F' + str(row + 1) + '= 0, 0, H' + str(row + 1) + '/F' + str(row + 1) + ')',
                                    f_percent)  # - % Crumbs
                sheet.write_formula(row, 14, '=IF(F' + str(row + 1) + '= 0, 0, (J' + str(row + 1) + ' * 60)/F' + str(
                    row + 1) + ')', f_data2d)  # - MO

                # Ind columns
                sheet.write_formula(row, 16, '=IF(L' + str(row + 1) + '= 0, 0, (K' + str(row + 1) + '/L' + str(
                    row + 1) + '/1.15) * 100)', f_percent)  # - IND Backs
                sheet.write_formula(row, 17, '=IF(O' + str(row + 1) + '= 0, 0, (P' + str(row + 1) + '/O' + str(
                    row + 1) + '/1.15))', f_percent)  # - IND MO
                sheet.write_formula(row, 18, '=IF(N' + str(row + 1) + '= 0, 0, (M' + str(row + 1) + '/N' + str(
                    row + 1) + '/1.15) * 100)', f_percent)  # - IND Crumbs
                sheet.write_formula(row, 19, '=I' + str(row + 1) + '/100', f_percent)  # - IND Quality
                sheet.write_formula(row, 20,
                                    '0.6 * Q' + str(row + 1) + ' + 0.3 * R' + str(row + 1) + ' + 0.1 * T' + str(
                                        row + 1), f_percent)  # - IND Cleaning

                wgross_weight_reference = 0
                wproduct_weight = 0
                wshared_product_weight = 0
                wsp1_weight = 0
                wtotquality = 0
                wtotal_hours = 0
                wnumreg = 0

            # grouped data vars
            wgross_weight_reference += obj.gross_weight_reference
            wproduct_weight += obj.product_weight
            wshared_product_weight += obj.shared_product_weight
            wsp1_weight += obj.sp1_weight
            wtotquality += obj.quality * (obj.product_weight + obj.shared_product_weight / 2)
            wtotal_hours += obj.total_hours
            wnumreg += 1

            if (wproduct_weight + wshared_product_weight / 2) == 0:
                wquality = 0
            else:
                wquality = wtotquality / (wproduct_weight + wshared_product_weight / 2)

            # columns with grouped data
            sheet.write(row, 5, wgross_weight_reference, f_data2d)
            sheet.write(row, 6, wproduct_weight, f_data2d)
            sheet.write(row, 7, wsp1_weight, f_data2d)
            sheet.write(row, 8, wquality, f_data2d)
            sheet.write(row, 9, wtotal_hours, f_data2d)

            wlot_name = obj.lot_name
            wemployee_code = obj.employee_code
            wworkstation_name = obj.workstation_name

            # Final Footer Row ------------------------------------------
            for numcol in range(0, 20):
                sheet.write(row + 1, numcol, '', f_footer)
            sheet.write_formula(row + 1, 5, '=SUM(F' + str(header_row + 1) + ':F' + str(row + 1) + ')', f_footer)
            sheet.write_formula(row + 1, 6, '=SUM(G' + str(header_row + 1) + ':G' + str(row + 1) + ')', f_footer)
            sheet.write_formula(row + 1, 7, '=SUM(H' + str(header_row + 1) + ':H' + str(row + 1) + ')', f_footer)
            sheet.write_formula(row + 1, 9, '=SUM(J' + str(header_row + 1) + ':J' + str(row + 1) + ')', f_footer)
            sheet.write_formula(row + 1, 11, '=AVERAGE(L' + str(header_row + 1) + ':L' + str(row + 1) + ')', f_footer)
            sheet.write_formula(row + 1, 13, '=AVERAGE(N' + str(header_row + 1) + ':N' + str(row + 1) + ')', f_footer)
            sheet.write_formula(row + 1, 15, '=AVERAGE(P' + str(header_row + 1) + ':P' + str(row + 1) + ')', f_footer)
            # formulation columns
            sheet.write_formula(row + 1, 8,
                                '=IF(F' + str(row + 2) + '= 0, 0 , SUMPRODUCT(I' + str(header_row + 1) + ':I' + str(
                                    row + 1) + ', F' + str(header_row + 1) + ':F' + str(row + 1) + ') / F' + str(
                                    row + 2) + ')', f_footer)
            sheet.write_formula(row + 1, 10,
                                '=IF(F' + str(row + 2) + '= 0, 0, G' + str(row + 2) + '/F' + str(row + 2) + ')',
                                f_footer_perc)  # - % Backs
            sheet.write_formula(row + 1, 12,
                                '=IF(F' + str(row + 2) + '= 0, 0, H' + str(row + 2) + '/F' + str(row + 2) + ')',
                                f_footer_perc)  # - % Crumbs
            sheet.write_formula(row + 1, 14,
                                '=IF(F' + str(row + 2) + '= 0, 0, (J' + str(row + 2) + ' * 60)/F' + str(row + 2) + ')',
                                f_footer)  # - MO
            # Ind columns
            sheet.write_formula(row + 1, 16, '=IF(L' + str(row + 2) + '= 0, 0, (K' + str(row + 2) + '/L' + str(
                row + 2) + '/1.15) * 100)', f_footer_perc)  # - IND Backs
            sheet.write_formula(row + 1, 17, '=IF(O' + str(row + 2) + '= 0, 0, (P' + str(row + 2) + '/O' + str(
                row + 2) + '/1.15))', f_footer_perc)  # - IND MO
            sheet.write_formula(row + 1, 18, '=IF(N' + str(row + 2) + '= 0, 0, (M' + str(row + 2) + '/N' + str(
                row + 2) + '/1.15) * 100)', f_footer_perc)  # - IND Crumbs
            sheet.write_formula(row + 1, 19, '=I' + str(row + 2) + '/100', f_footer_perc)  # - IND Quality
            sheet.write_formula(row + 1, 20,
                                '0.6 * Q' + str(row + 2) + ' + 0.3 * R' + str(row + 2) + ' + 0.1 * T' + str(row + 2),
                                f_footer_perc)  # - IND Cleaning
            """
            sheet.write_formula(row + 1, 16,
                                '=IF(F' + str(row + 2) + '= 0, 0 , SUMPRODUCT(Q' + str(header_row + 1) + ':Q' + str(
                                    row + 1) + ', F' + str(header_row + 1) + ':F' + str(row + 1) + ') / F' + str(
                                    row + 2) + ')', f_footer_perc)  # - IND Backs
            sheet.write_formula(row + 1, 17,
                                '=IF(F' + str(row + 2) + '= 0, 0 , SUMPRODUCT(R' + str(header_row + 1) + ':R' + str(
                                    row + 1) + ', F' + str(header_row + 1) + ':F' + str(row + 1) + ') / F' + str(
                                    row + 2) + ')', f_footer_perc)  # - IND MO
            sheet.write_formula(row + 1, 18,
                                '=IF(F' + str(row + 2) + '= 0, 0 , SUMPRODUCT(S' + str(header_row + 1) + ':S' + str(
                                    row + 1) + ', F' + str(header_row + 1) + ':F' + str(row + 1) + ') / F' + str(
                                    row + 2) + ')', f_footer_perc)  # - IND Crumbs
            sheet.write_formula(row + 1, 19, '=I' + str(row + 2) + '/100', f_footer_perc)  # - IND Quality
            sheet.write_formula(row + 1, 20,
                                '=IF(F' + str(row + 2) + '= 0, 0 , SUMPRODUCT(U' + str(header_row + 1) + ':U' + str(
                                    row + 1) + ', F' + str(header_row + 1) + ':F' + str(row + 1) + ') / F' + str(
                                    row + 2) + ')', f_footer_perc)  # - IND Cleaning
            """

            # Write Filter -----------------------------------------------
            # sheet.write(2, 2, datetime.datetime.now(), f_filter)
            # datefilter = _("Date From: %s to %s") % (wstart_date, wend_date)
            # if wstart_date == wend_date:
            #    datefilter = _("Date: %s") % wstart_date
            # if wlot_filter_uniq:
            #    datefilter = datefilter + ' // ' + _("Lot: %s") % wlot_filter
            #    datefilter = datefilter + ' // ' + _("%.2f Kg Frozen") % wgross_frozen
            # if wshift_filter_uniq:
            #    datefilter = datefilter + ' // ' + _("Shift: %s") % wshift_filter
            # sheet.write(2, 2, datefilter, f_filter)
            # if wlot_filter_uniq:
            #    sheet.write(3, 2, product_name, f_filter)

        # Final Presentation
        # Select the cells back to image & zoom presentation & split & freeze_panes
        sheet.set_selection('A6')
        sheet.set_zoom(80)
        # sheet.split_panes(60,0,5,0)


class ReportRptCumulativeXlsx(models.AbstractModel):
    _name = 'report.mdc.rpt_cumulative'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, rpt_cumulative):
        report_name = "rpt_cumulative"
        sheet = workbook.add_worksheet("Cumulative Report")

        #retrieve rpt_hide_shift_change_data parameter
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
        f_filter = workbook.add_format(f_cells["filter"])
        f_percent = workbook.add_format(f_cells ["percent"])
        f_data = workbook.add_format(f_cells ["data"])
        f_data2d = workbook.add_format(f_cells["data2d"])
        f_footer = workbook.add_format(f_cells["footer"])

        # Set columns widths
        sheet.set_column('A:X', 13)
        sheet.set_column('O:S', 0, None, {'hidden': 1})
        sheet.set_column('B:B', 40) # Employee name
        if hide_shift_data:
            sheet.set_column('F:H', 0, None, {'hidden': 1})

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
        sheet.write(1, 2, _("CUMULATIVE REPORT"), f_title)

        # write Filter
        sheet.write(2, 2, _("Date From:"), f_filter)

        header_row = 5
        header_row_str = str(header_row + 1)
        # write column header ----------------------------------------
        sheet.write('A' + header_row_str, _("Employee Code"), f_header) # - 0
        sheet.write('B' + header_row_str, _("Employee Name"), f_header)
        sheet.write('C' + header_row_str, _("Gross"), f_header)
        sheet.write('D' + header_row_str, _("Backs"), f_header)
        sheet.write('E' + header_row_str, _("Crumbs"), f_header)
        sheet.write('F' + header_row_str, _("Shift Change Gross"), f_header) # - 5
        sheet.write('G' + header_row_str, _("Shift Change Backs"), f_header)
        sheet.write('H' + header_row_str, _("Shift Change Crumbs"), f_header)
        sheet.write('I' + header_row_str, _("Quality"), f_header)
        sheet.write('J' + header_row_str, _("% Backs"), f_header)
        sheet.write('K' + header_row_str, _("% Crumbs"), f_header) # - 10
        sheet.write('L' + header_row_str, _("% Total Yield"), f_header)
        sheet.write('M' + header_row_str, _("Waste"), f_header)
        sheet.write('N' + header_row_str, _("% Waste"), f_header)
        sheet.write('O' + header_row_str, _("Time"), f_header)
        sheet.write('P' + header_row_str, _("MO."), f_header) # - 15
        sheet.write('Q' + header_row_str, _("STD Back"), f_header)
        sheet.write('R' + header_row_str, _("STD Crumbs"), f_header)
        sheet.write('S' + header_row_str, _("STD MO"), f_header)
        sheet.write('T' + header_row_str, _("IND Backs"), f_header_ind)
        sheet.write('U' + header_row_str, _("IND MO"), f_header_ind) # - 20
        sheet.write('V' + header_row_str, _("IND Crumbs"), f_header_ind)
        sheet.write('W' + header_row_str, _("IND Quality"), f_header_ind)
        sheet.write('X' + header_row_str, _("IND Cleaning"), f_header_ind)
        # -------------------------------------------------------

        # TODO alternate dict list with almost grouped data (still problems with product and date)

        # write data rows
        row=header_row
        wlot_name = ''
        wemployee_code = ''
        wgross_weight = 0
        wproduct_weight = 0
        wsp1_weight = 0
        wshared_gross_weight = 0
        wshared_product_weight = 0
        wshared_sp1_weight = 0
        wquality = 0
        wtotquality = 0
        wtotal_hours = 0
        wnumreg = 0
        # Filters ---------
        wstart_date = False
        wend_date = False
        wlot_filter = ''
        wlot_filter_uniq = True
        # -----------------

        for obj in rpt_cumulative:

            # Filters: ----------------------------------------
            # min a max date
            if wstart_date is False or wstart_date > obj.create_date:
                wstart_date = obj.create_date
            if wend_date is False or wend_date < obj.create_date:
                wend_date = obj.create_date
            # lot
            if wlot_filter == '':
                wlot_filter = obj.lot_name
            # ------------------------------------------------

            # lot Filter
            if wlot_filter != obj.lot_name:
                wlot_filter_uniq = False

            if (wemployee_code != obj.employee_code):

                row = row + 1

                # direct data from view database
                sheet.write(row, 0, obj.employee_code, f_data)
                sheet.write(row, 1, obj.employee_name, f_data)

                # std columns
                sheet.write(row, 16, obj.std_yield_product, f_data2d)
                sheet.write(row, 17, obj.std_yield_sp1, f_data2d)
                sheet.write(row, 18, obj.std_speed, f_data2d)
                # formulation columns
                sheet.write_formula(row, 9, '=IF(C' + str(row + 1) + '= 0, 0, D' + str(row + 1) + '/C' + str(row + 1) + ')', f_percent)  # - % Backs
                sheet.write_formula(row, 10, '=IF(C' + str(row + 1) + '= 0, 0, E' + str(row + 1) + '/C' + str(row + 1) + ')', f_percent)  # - % Crumbs
                sheet.write_formula(row, 11, '=IF(C' + str(row + 1) + '= 0, 0, (D' + str(row + 1) + '+E' + str(row + 1) + ')/C' + str(row + 1) + ')', f_percent) # - % Total Yield
                sheet.write_formula(row, 12, '=(C' + str(row + 1) + '-D' + str(row + 1) + '-E' + str(row + 1) + ')',  f_data2d)  # - Waste
                sheet.write_formula(row, 13, '=IF(C' + str(row + 1) + '= 0, 0, (M' + str(row + 1) + ')/C' + str(row + 1) + ')', f_percent)  # - % Waste
                sheet.write_formula(row, 15, '=IF(C' + str(row + 1) + '= 0, 0, (O' + str(row + 1) + ' * 60)/C' + str(row + 1) + ')', f_data2d)  # - MO
                # Ind columns
                sheet.write_formula(row, 19, '=IF(Q' + str(row + 1) + '= 0, 0, (J' + str(row + 1) + '/Q' + str(row + 1) + '/1.15) * 100)', f_percent)  # - IND Backs
                sheet.write_formula(row, 20, '=IF(P' + str(row + 1) + '= 0, 0, (S' + str(row + 1) + '/P' + str(row + 1) + '/1.15))', f_percent)  # - IND MO
                sheet.write_formula(row, 21, '=IF(R' + str(row + 1) + '= 0, 0, (K' + str(row + 1) + '/R' + str(row + 1) + '/1.15) * 100)', f_percent)  # - IND Crumbs
                sheet.write_formula(row, 22, '=I' + str(row + 1)+'/100', f_percent)  # - IND Quality
                sheet.write_formula(row, 23, '0.6 * T' + str(row + 1) + ' + 0.3 * U' + str(row + 1) + ' + 0.1 * W' + str(row + 1), f_percent)  # - IND Cleaning

                wgross_weight = 0
                wproduct_weight = 0
                wsp1_weight = 0
                wshared_gross_weight = 0
                wshared_product_weight = 0
                wshared_sp1_weight = 0
                wtotquality = 0
                wtotal_hours = 0
                wnumreg = 0

            # grouped data vars
            wgross_weight += obj.gross_weight
            wproduct_weight += obj.product_weight
            wsp1_weight += obj.sp1_weight
            wshared_gross_weight += obj.shared_gross_weight
            wshared_product_weight += obj.shared_product_weight
            wshared_sp1_weight += obj.shared_sp1_weight
            wtotquality += obj.quality * (obj.product_weight + obj.shared_product_weight /2)
            wtotal_hours += obj.total_hours
            wnumreg += 1

            if (wproduct_weight + wshared_product_weight/2) == 0:
                wquality=0
            else:
                wquality = wtotquality/(wproduct_weight + wshared_product_weight/2)

            #columns with grouped data
            sheet.write(row, 2, wgross_weight, f_data2d)
            sheet.write(row, 3, wproduct_weight, f_data2d)
            sheet.write(row, 4, wsp1_weight, f_data2d)
            sheet.write(row, 5, wshared_gross_weight, f_data2d)
            sheet.write(row, 6, wshared_product_weight, f_data2d)
            sheet.write(row, 7, wshared_sp1_weight, f_data2d)
            sheet.write(row, 8, wquality, f_data2d)
            sheet.write(row, 14, wtotal_hours, f_data2d)

            wlot_name = obj.lot_name
            wemployee_code = obj.employee_code


            # Final Footer Row

        # write Filter
        datefilter = _("Date From: %s to %s") % (wstart_date, wend_date)
        if wstart_date == wend_date:
            datefilter = _("Date: #%s") % wstart_date
        sheet.write(2, 2, datefilter, f_filter)

        # Final Presentation
        # Select the cells back to image & zoom presentation & split & freeze_panes
        sheet.set_selection('A6')
        sheet.set_zoom(80)
        # sheet.split_panes(60,0,5,0)