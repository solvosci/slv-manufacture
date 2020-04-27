# -*- coding: utf-8 -*-
from odoo import fields, tools, models, _
from odoo.addons.mdc.report import report_xlsx
import base64
import tempfile


def formats():
    return {
        **report_xlsx.formats()
    }


class ReportRptIndicatorsByEmployeeXlsx(models.AbstractModel):
    _name = 'report.mdc.rpt_indicators_by_employee'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, rpt_indicators_by_employee):
        report_name = "rpt_indicators_by_employee"
        sheet = workbook.add_worksheet("Indicators by Employee Report")

        # General sheet style
        sheet.set_landscape()
        sheet.repeat_rows(0, 5)
        sheet.hide_gridlines(3)

        # get Formats Dictionary from standard function formats
        f_cells = formats()
        f_title = workbook.add_format(f_cells["title"])
        f_header = workbook.add_format(f_cells["header"])
        f_header_ind = workbook.add_format(f_cells["header_ind"])
        f_filter = workbook.add_format(f_cells["filter_date"])
        f_percent = workbook.add_format(f_cells["percent"])
        f_data = workbook.add_format(f_cells["data"])
        f_data2d = workbook.add_format(f_cells["data2d"])
        f_footer = workbook.add_format(f_cells["footer"])
        f_footer_perc = workbook.add_format(f_cells["footer_perc"])

        # Set columns widths
        sheet.set_column('A:H', 13)
        sheet.set_column('B:B', 40)  # Employee name
        sheet.set_column('I:I', 0)  # Col contains gross_weight_reference to calculate ponderated average into footer row

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
        sheet.write(1, 2, _("INDICATORS REPORT"), f_title)

        # write Filter
        sheet.write(2, 2, _("Date From:"), f_filter)

        header_row = 5
        header_row_str = str(header_row + 1)
        # write column header ----------------------------------------
        sheet.write('A' + header_row_str, _("Employee Code"), f_header)  # - 0
        sheet.write('B' + header_row_str, _("Employee Name"), f_header)
        sheet.write('C' + header_row_str, _("IND Backs"), f_header_ind)
        sheet.write('D' + header_row_str, _("IND MO"), f_header_ind)
        sheet.write('E' + header_row_str, _("IND Crumbs"), f_header_ind)
        sheet.write('F' + header_row_str, _("IND Quality"), f_header_ind)  # - 5
        sheet.write('G' + header_row_str, _("IND Cleaning"), f_header_ind)
        # -------------------------------------------------------

        # TODO alternate dict list with almost grouped data (still problems with product and date)

        # write data rows
        row = header_row
        wemployee_code = ''
        wind_backs_weight = 0
        wind_mo_weight = 0
        wind_crumbs_weight = 0
        wind_quality_weight = 0
        wind_cleaning_weight = 0
        wgross_weight_reference = 0

        # Filters ---------
        wstart_date = False
        wend_date = False
        wshift_filter = ''
        wshift_filter_uniq = True
        wline_filter = ''
        wline_filter_uniq = True
        # -----------------

        # we order the result in case changed the order in the view
        rpt_indicators_by_employee_sorted = rpt_indicators_by_employee.sorted("employee_code")

        for obj in rpt_indicators_by_employee_sorted:

            # Filters: ----------------------------------------
            # min a max date
            if wstart_date is False or wstart_date > obj.create_date:
                wstart_date = obj.create_date
            if wend_date is False or wend_date < obj.create_date:
                wend_date = obj.create_date
            # shift
            if wshift_filter == '':
                wshift_filter = obj.shift_code
            # line
            if wline_filter == '':
                wline_filter = obj.line_code
            # ------------------------------------------------

            # shift Filter
            if wshift_filter != obj.shift_code:
                wshift_filter_uniq = False
            # Line Filter
            if wline_filter != obj.line_code:
                wline_filter_uniq = False

            if (wemployee_code != obj.employee_code):
                row = row + 1

                # direct data from view database
                sheet.write(row, 0, obj.employee_code, f_data)
                sheet.write(row, 1, obj.employee_name, f_data)

                wind_backs_weight = 0
                wind_mo_weight = 0
                wind_crumbs_weight = 0
                wind_quality_weight = 0
                wind_cleaning_weight = 0
                wgross_weight_reference = 0

            # grouped data vars

            wind_backs_weight += obj.ind_backs * (obj.gross_weight_reference)
            wind_mo_weight += obj.ind_mo * (obj.gross_weight_reference)
            wind_crumbs_weight += obj.ind_crumbs * (obj.gross_weight_reference)
            wind_quality_weight += obj.ind_quality * (obj.gross_weight_reference)
            wind_cleaning_weight += obj.ind_cleaning * (obj.gross_weight_reference)
            wgross_weight_reference += obj.gross_weight_reference

            if (wgross_weight_reference) == 0:
                res_wind_backs_weight = 0
                res_wind_mo_weight = 0
                res_wind_crumbs_weight = 0
                res_wind_quality_weight = 0
                res_wind_cleaning_weight = 0
            else:
                res_wind_backs_weight = wind_backs_weight / (wgross_weight_reference * 100)
                res_wind_mo_weight = wind_mo_weight / (wgross_weight_reference * 100)
                res_wind_crumbs_weight = wind_crumbs_weight / (wgross_weight_reference * 100)
                res_wind_quality_weight = wind_quality_weight / (wgross_weight_reference * 100)
                res_wind_cleaning_weight = wind_cleaning_weight / (wgross_weight_reference * 100)

            # columns with grouped data - indicators
            sheet.write(row, 2, res_wind_backs_weight, f_percent)
            sheet.write(row, 3, res_wind_mo_weight, f_percent)
            sheet.write(row, 4, res_wind_crumbs_weight, f_percent)
            sheet.write(row, 5, res_wind_quality_weight, f_percent)
            sheet.write(row, 6, res_wind_cleaning_weight, f_percent)

            # -- Hidden col contains gross_weight_reference to calculate ponderated average into footer row
            sheet.write(row, 8, wgross_weight_reference, f_data2d)

            wemployee_code = obj.employee_code

            # Final Footer Row ------------------------------------------
            for numcol in range(0, 3):
                sheet.write(row + 1, numcol, '', f_footer)

            # formulation columns - indicators
            sheet.write_formula(row + 1, 8, '=SUM(I' + str(header_row + 1) + ':I' + str(row + 1) + ')', f_footer)
            sheet.write_formula(row + 1, 2,
                                '=IF(I' + str(row + 2) + '= 0, 0 , SUMPRODUCT(C' + str(header_row + 1) + ':C' + str(
                                    row + 1) + ', I' + str(header_row + 1) + ':I' + str(row + 1) + ') / I' + str(
                                    row + 2) + ')', f_footer_perc)
            sheet.write_formula(row + 1, 3,
                                '=IF(I' + str(row + 2) + '= 0, 0 , SUMPRODUCT(D' + str(header_row + 1) + ':D' + str(
                                    row + 1) + ', I' + str(header_row + 1) + ':I' + str(row + 1) + ') / I' + str(
                                    row + 2) + ')', f_footer_perc)
            sheet.write_formula(row + 1, 4,
                                '=IF(I' + str(row + 2) + '= 0, 0 , SUMPRODUCT(E' + str(header_row + 1) + ':E' + str(
                                    row + 1) + ', I' + str(header_row + 1) + ':I' + str(row + 1) + ') / I' + str(
                                    row + 2) + ')', f_footer_perc)
            sheet.write_formula(row + 1, 5,
                                '=IF(I' + str(row + 2) + '= 0, 0 , SUMPRODUCT(F' + str(header_row + 1) + ':F' + str(
                                    row + 1) + ', I' + str(header_row + 1) + ':I' + str(row + 1) + ') / I' + str(
                                    row + 2) + ')', f_footer_perc)
            sheet.write_formula(row + 1, 6,
                                '=IF(I' + str(row + 2) + '= 0, 0 , SUMPRODUCT(G' + str(header_row + 1) + ':G' + str(
                                    row + 1) + ', I' + str(header_row + 1) + ':I' + str(row + 1) + ') / I' + str(
                                    row + 2) + ')', f_footer_perc)

            # Write Filter -----------------------------------------------
            datefilter = _("Date From: %s to %s") % (wstart_date, wend_date)
            if wstart_date == wend_date:
                datefilter = _("Date: #%s") % wstart_date
            if wshift_filter_uniq:
                datefilter = datefilter + ' // ' + _("Shift: %s") % wshift_filter
            if wline_filter_uniq:
                datefilter = datefilter + ' // ' + _("Line: %s") % wline_filter

            sheet.write(2, 2, datefilter, f_filter)

        # Final Presentation
        # Select the cells back to image & zoom presentation & split & freeze_panes
        sheet.set_selection('A6')
        sheet.set_zoom(80)
        # sheet.split_panes(60,0,5,0)