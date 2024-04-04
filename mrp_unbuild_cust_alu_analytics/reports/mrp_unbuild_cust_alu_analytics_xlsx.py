# © 2024 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3.0 (https://www.gnu.org/licenses/agpl-3.0.html)

from odoo import fields, models, _
from datetime import datetime, date
import openpyxl.utils


class MrpUnbuildCustAluAnalyticsXlsx(models.AbstractModel):
    _name = 'report.mrp_unbuild_cust_alu_analytics.mpr_unbuild_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, order):
        #Add styles and formats
        header_format = workbook.add_format(
            {
                'bold': True,
                'font_color': '#000000',
                'bg_color': '#f76060',
                'font_name': 'Arial',
                'border': 5,
                'font_size': 12,
                'align': 'left'
            }
        )
        header_format_2 = workbook.add_format(
            {
                'bold': True,
                'font_color': '#000000',
                'bg_color': '#ff7777',
                'font_name': 'Arial',
                'border': 5,
                'font_size': 12,
                'align': 'left'
            }
        )
        header_format_3 = workbook.add_format(
            {
                'bold': True,
                'font_color': '#000000',
                'bg_color': '#ff9393',
                'font_name': 'Arial',
                'border': 5,
                'font_size': 12,
                'align': 'left'
            }
        )
        header_format_4 = workbook.add_format(
            {
                'bold': True,
                'font_color': '#000000',
                'bg_color': '#fcaeae',
                'font_name': 'Arial',
                'border': 5,
                'font_size': 12,
                'align': 'left'
            }
        )
        header_format_5 = workbook.add_format(
            {
                'bold': True,
                'font_color': '#000000',
                'font_name': 'Arial',
                'border': 5,
                'font_size': 12,
                'align': 'left'
            }
        )
        subheader_format = workbook.add_format(
            {
                'bold': True,
                'font_color': '#000000',
                'border': 1,
                'font_size': 11,
                'align': 'left'
            }
        )
        subheader_footer_format = workbook.add_format(
            {
                'bold': True,
                'font_color': '#000000',
                'border': 3,
                'font_size': 12,
                'align': 'left',
                'bg_color': '#ffb2b2'
            }
        )
        products_format = workbook.add_format(
            {
                'bold': True,
                'font_color': '#210000',
                'font_size': 11,
                'font_name': 'Arial',
                'align': 'left',
                'border': 1
            }
        )
        datetime_format = workbook.add_format(
            {
                'align': 'left',
                'num_format': 'dd/mm/yy',
                'border': 1
            }
        )
        datetime_header_format = workbook.add_format(
            {
                'bold': True,
                'border': 1,
                'align': 'left',
                'num_format': 'dd/mm/yy'
            }
        )
        time_format = workbook.add_format(
            {
                'align': 'right',
                'num_format': 'hh:mm'
            }
        )
        time_format = workbook.add_format(
            {
                'align': 'right',
                'num_format': 'hh:mm',
                'border': 1
            }
        )
        float_format = workbook.add_format(
            {
                'align': 'right',
                'num_format': '0.00',
                'border': 1
            }
        )
        float_extend_format = workbook.add_format(
            {
                'align': 'right',
                'num_format': '0.00000',
                'border': 1,
                'bold': True,
            }
        )
        float_footer_format = workbook.add_format(
            {
                'align': 'right',
                'num_format': '0.00',
                'border': 3,
                'bold': True,
                'font_size': 11,
                'bg_color': '#ffb2b2'
            }
        )
        int_format = workbook.add_format(
            {
                'align': 'right',
                'num_format': '0',
                'border': 1
            }
        )
        string_format = workbook.add_format(
            {
                'align': 'left',
                'border': 1
            }
        )


        # Get unique combination of product_id process_type_id
        unique_orders = set()
        unique_orders = {(order.product_id, order.process_type_id) for order in order}
        list_unique_orders = []
        for product_id, process_type_id in unique_orders:
            list_unique_orders += [list(filter(lambda x: x.product_id.id == product_id.id and x.process_type_id.id == process_type_id.id, order))]


        # Iterate over each combination, and add a sheet for each combination
        for unique_list in list_unique_orders:
            sheet = workbook.add_worksheet("%s-%s" % (unique_list[0].product_id.default_code, unique_list[0].process_type_id.name))

            # Set column width
            sheet.set_column('A:ZZ', 22)
            total_products = 0
            z = 2 # each unbuild_id
            for record in unique_list:
                all_product_total_qty = sum(record.bom_quants_total_ids.mapped("total_qty"))
                total_products = len(record.bom_quants_total_ids) if len(record.bom_quants_total_ids) > total_products else total_products
                total_products_and_percentage = int(total_products * 2)
                sheet.write(1, 0, _('Date'), subheader_format)
                sheet.write(0, 0, record.product_id.default_code, header_format)
                sheet.write(z, 0, record.unbuild_date, datetime_header_format)
                sheet.write(0, total_products_and_percentage + 2, _('Start Date'), header_format_3)
                sheet.write(z, total_products_and_percentage + 2, record.shift_start_date if record.shift_start_date != False else "", datetime_format)
                sheet.write(0, total_products_and_percentage + 3, _('End Date'), header_format_3)
                sheet.write(z, total_products_and_percentage + 3, record.shift_end_date if record.shift_end_date != False else "", datetime_format)
                sheet.write(0, total_products_and_percentage + 4, _('Start Hour'), header_format_3)
                sheet.write(z, total_products_and_percentage + 4, record.shift_start_date if record.shift_start_date != False else "", time_format)
                sheet.write(0, total_products_and_percentage + 5, _('End Hour'), header_format_3)
                sheet.write(z, total_products_and_percentage + 5, record.shift_end_date if record.shift_end_date != False else "", time_format)
                sheet.write(0, total_products_and_percentage + 6, _('Break Time'), header_format_3)
                sheet.write(z, total_products_and_percentage + 6, record.shift_break_time * 60 if record.shift_break_time != False else "", int_format)
                sheet.write(0, total_products_and_percentage + 7, _('Rest Break Time'), header_format_3)
                sheet.write(z, total_products_and_percentage + 7, record.shift_stop_time * 60 if record.shift_stop_time != False else "", int_format)
                sheet.write(0, total_products_and_percentage + 8, _('Gross Time'), header_format_3)
                sheet.write(z, total_products_and_percentage + 8, record.shift_total_time if record.shift_total_time != False else "", float_format)
                sheet.write(0, total_products_and_percentage + 9, _('Net Time'), header_format_3)
                sheet.write(z, total_products_and_percentage + 9, record.shift_total_time - record.shift_break_time - record.shift_stop_time if record.shift_total_time != False else "", float_format)
                sheet.write(0, total_products_and_percentage + 10, _('TM/h Gross'), header_format_3)
                sheet.write(z, total_products_and_percentage + 10, all_product_total_qty / record.shift_total_time if record.shift_total_time != False else "", float_format)
                sheet.write(0, total_products_and_percentage + 11, _('TM/h Net'), header_format_3)
                sheet.write(z, total_products_and_percentage + 11, all_product_total_qty / (record.shift_total_time - record.shift_break_time - record.shift_stop_time) if record.shift_total_time != False else "", float_format)
                tag_names = ', '.join(tag.name for tag in record.tag_ids)
                sheet.write(0, total_products_and_percentage + 12, _('Tags'), header_format_4)
                sheet.write(z, total_products_and_percentage + 12, tag_names, string_format)
                sheet.write(0, total_products_and_percentage + 13, _('Comments'), header_format_4)
                sheet.write(z, total_products_and_percentage + 13, record.notes if record.notes != False else "", string_format)
                sheet.write(0, total_products_and_percentage + 14, _('Analytics'), header_format_4)
                sheet.write(z, total_products_and_percentage + 14, _("Yes") if record.analytic_ids else _("No"), string_format)
                sheet.write(z, 1 + total_products, all_product_total_qty, float_format)
                j = 0
                if record.analytic_ids:
                    for inspection_line in record.analytic_ids[0].inspection_lines:
                        j += 1
                        sheet.write(0, total_products_and_percentage + 14 + j, inspection_line.name, header_format_5)
                        sheet.write(z, total_products_and_percentage + 14 + j, inspection_line.quantitative_value, float_extend_format)
                y = 1
                for product in record.bom_quants_total_ids:
                    sheet.write(0, y, product.bom_line_id.product_id.default_code, header_format)
                    sheet.write(0, y + total_products + 1, "%\n" + product.bom_line_id.product_id.default_code, header_format_2)
                    sheet.write(1, y, product.bom_line_id.product_id.name, products_format)
                    sheet.write(1, y + total_products + 1, product.bom_line_id.product_id.name, products_format)
                    sheet.write(z, y, product.total_qty, float_format)
                    sheet.write(z, y + total_products + 1, product.total_qty_percentage * 100, float_format)
                    y += 1
                z += 1
            sheet.write(0, 1 + total_products, _('Total'), header_format)

            #TOTALS
            sheet.write(z, 0, _('TOTAL'), subheader_footer_format)
            for i in range(1, y + 1):
                column = openpyxl.utils.get_column_letter(i + 1)
                sheet.write_formula(z, i, '=SUMPRODUCT(' + column + '3' + ':' + column + str(z) + ')', float_footer_format)

            sheet.set_zoom(100)
