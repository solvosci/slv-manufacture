# © 2024 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3.0 (https://www.gnu.org/licenses/agpl-3.0.html)

from odoo import fields, models, _
import openpyxl.utils
from datetime import datetime


class MrpUnbuildCustAluAnalyticsXlsx(models.AbstractModel):
    _name = 'report.mrp_unbuild_cust_alu_analytics.mpr_unbuild_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def get_name(self, product_id):
        return (
            product_id.display_name if not product_id.default_code
            else product_id.display_name.split("[%s]" % product_id.default_code)[1].lstrip()
        )

    def generate_xlsx_report(self, workbook, data, order):
        #Add styles and formats
        #region
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
        #endregion


        # Get unique combination of product_id process_type_id
        unique_orders = set()
        unique_orders = {(order.product_id, order.process_type_id) for order in order}
        list_unique_orders = []
        for product_id, process_type_id in unique_orders:
            list_unique_orders += [list(filter(lambda x: x.product_id.id == product_id.id and x.process_type_id.id == process_type_id.id, order))]


        # Create a Sheet for each unqiue combination 
        for unique_list in list_unique_orders:
            sheet = workbook.add_worksheet("%s-%s" % (unique_list[0].product_id.default_code, unique_list[0].process_type_id.name))

            # Set column width
            sheet.set_column('A:ZZ', 22)
            total_products = 0 # Reinitialize total_products

            z = 2 # each unbuild_id
            unique_products = []

            # Get list of unique products
            for record in unique_list:
                if unique_products == []:
                    unique_products = record.bom_quants_total_ids.bom_line_ids.mapped("product_id.id")
                else:
                    extra_unique_products = record.bom_quants_total_ids.bom_line_ids.mapped("product_id.id")
                    unique_products = list(dict.fromkeys(unique_products + extra_unique_products))
            total_products = len(unique_products)

            # Set borders to product cells
            for col in range(total_products * 2 + 4):
                for row in range(len(unique_list) + 2):
                    sheet.write(row, col, None, products_format)

            for record in unique_list:
                all_product_total_qty = record._get_product_qty_from_bom_totals()
                total_products_and_percentage = int(total_products * 2) # Get post percentage cells position
                sheet.write(1, 0, _('Date'), subheader_format)
                sheet.write(0, 1, _('Unbuilds'), header_format)
                sheet.write(0, 0, record.product_id.default_code, header_format)
                sheet.write(z, 0, record.unbuild_date, datetime_header_format)
                sheet.write(z, 1, record.name, subheader_format)

                #STATIC INFO
                sheet.write(0, total_products_and_percentage + 3, _('Start Date'), header_format_3)
                sheet.write(z, total_products_and_percentage + 3, fields.Datetime.context_timestamp(self.env.user, record.shift_start_date).replace(tzinfo=None) if record.shift_start_date != False else "", datetime_format)
                sheet.write(0, total_products_and_percentage + 4, _('End Date'), header_format_3)
                sheet.write(z, total_products_and_percentage + 4, fields.Datetime.context_timestamp(self.env.user, record.shift_end_date).replace(tzinfo=None) if record.shift_end_date != False else "", datetime_format)
                sheet.write(0, total_products_and_percentage + 5, _('Start Hour'), header_format_3)
                sheet.write(z, total_products_and_percentage + 5, fields.Datetime.context_timestamp(self.env.user, record.shift_start_date).replace(tzinfo=None) if record.shift_start_date != False else "", time_format)
                sheet.write(0, total_products_and_percentage + 6, _('End Hour'), header_format_3)
                sheet.write(z, total_products_and_percentage + 6, fields.Datetime.context_timestamp(self.env.user, record.shift_end_date).replace(tzinfo=None) if record.shift_end_date != False else "", time_format)
                sheet.write(0, total_products_and_percentage + 7, _('Break Time'), header_format_3)
                sheet.write(z, total_products_and_percentage + 7, '{0:02.0f}:{1:02.0f}'.format(*divmod(record.shift_break_time * 60, 60)) if record.shift_break_time != False else "", time_format)
                sheet.write(0, total_products_and_percentage + 8, _('Rest Break Time'), header_format_3)
                sheet.write(z, total_products_and_percentage + 8, '{0:02.0f}:{1:02.0f}'.format(*divmod(record.shift_stop_time * 60, 60)) if record.shift_stop_time != False else "", time_format)
                sheet.write(0, total_products_and_percentage + 9, _('Scheduled Time'), header_format_3)
                sheet.write(z, total_products_and_percentage + 9, record.scheduled_time if record.scheduled_time != False else "", float_format)
                sheet.write(0, total_products_and_percentage + 10, _('Gross Time'), header_format_3)
                sheet.write(z, total_products_and_percentage + 10, record.shift_total_time if record.shift_total_time != False else "", float_format)
                sheet.write(0, total_products_and_percentage + 11, _('Net Time'), header_format_3)
                sheet.write(z, total_products_and_percentage + 11, record.shift_total_time - record.shift_break_time - record.shift_stop_time if record.shift_total_time != False else "", float_format)
                sheet.write(0, total_products_and_percentage + 12, _('TM/h Gross'), header_format_3)
                sheet.write(z, total_products_and_percentage + 12, all_product_total_qty / record.shift_total_time if record.shift_total_time != False else "", float_format)
                sheet.write(0, total_products_and_percentage + 13, _('TM/h Net'), header_format_3)
                sheet.write(z, total_products_and_percentage + 13, all_product_total_qty / (record.shift_total_time - record.shift_break_time - record.shift_stop_time) if record.shift_total_time != False else "", float_format)
                tag_names = ', '.join(tag.name for tag in record.tag_ids)
                sheet.write(0, total_products_and_percentage + 14, _('Tags'), header_format_4)
                sheet.write(z, total_products_and_percentage + 14, tag_names, string_format)
                sheet.write(0, total_products_and_percentage + 15, _('Comments'), header_format_4)
                sheet.write(z, total_products_and_percentage + 15, record.notes if record.notes != False else "", string_format)
                sheet.write(0, total_products_and_percentage + 16, _('Analytics'), header_format_4)
                sheet.write(z, total_products_and_percentage + 16, _("Yes") if record.analytic_ids else _("No"), string_format)
                sheet.write(z, 2 + total_products, all_product_total_qty, float_format)

                #ANALYTICS
                j = 0 #Index for each analytic
                if record.analytic_ids:
                    for inspection_line in record.analytic_ids[0].inspection_lines:
                        j += 1
                        sheet.write(0, total_products_and_percentage + 16 + j, inspection_line.name, header_format_5)
                        if inspection_line.minor:
                            sheet.write(z, total_products_and_percentage + 16 + j, "<" + str(inspection_line.quantitative_value), float_extend_format)
                        else:
                            sheet.write(z, total_products_and_percentage + 16 + j, inspection_line.quantitative_value, float_extend_format)
                y = 2

                #PRODUCTS AND PERCENTAGE
                #Headers
                for unique_product in unique_products:
                    unique_product = self.env["product.product"].browse(unique_product)
                    sheet.write(0, y, unique_product.default_code if unique_product.default_code != False else "", header_format)
                    sheet.write(0, y + total_products + 1, "%\n" + unique_product.default_code if unique_product.default_code != False else "", header_format_2)
                    sheet.write(1, y, self.get_name(unique_product), products_format)
                    sheet.write(1, y + total_products + 1, unique_product.name, products_format)
                    y += 1
                j = 2
                #Data
                for product in record.bom_quants_total_ids:
                    index = j + unique_products.index(product.bom_line_id.product_id.id)
                    sheet.write(z, index, product.total_qty, float_format)
                    sheet.write(z, index + total_products + 1, product.total_qty_percentage * 100, float_format)
                y += total_products
                z += 1
            sheet.write(0, 2 + total_products, _('Total'), header_format)

            #FOOTER
            sheet.merge_range("A%s:B%s" % (z + 1, z + 1), '', subheader_footer_format)
            sheet.write(z, 0, _('TOTAL'), subheader_footer_format)
            for i in range(2, y + 1):
                column = openpyxl.utils.get_column_letter(i + 1)
                sheet.write_formula(z, i, '=SUM(' + column + '3' + ':' + column + str(z) + ')', float_footer_format)

            sheet.set_zoom(100)
