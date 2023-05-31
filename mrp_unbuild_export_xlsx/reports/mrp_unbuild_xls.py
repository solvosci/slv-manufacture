# © 2023 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html

from odoo import fields, models, _
from datetime import datetime, date


class MrpUnbuildXLS(models.AbstractModel):
    _name = 'report.mrp_unbuild_export_xlsx.mpr_unbuild_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, order):
        for record in order:
            sheet = workbook.add_worksheet(record.name)
            bold_format = workbook.add_format({'bold': True,
                                               'font_color': '#004080',
                                               'size': 16})
            percent_format = workbook.add_format({'num_format': '0.00%'})
            datetime_format = workbook.add_format({'num_format': 'dd/mm/yy hh:mm:ss'})

            sheet.write(0, 0, _('Product'), bold_format)
            sheet.write(0, 1, _('Description'), bold_format)
            sheet.write(0, 2, _('Quantity'), bold_format)
            sheet.write(1, 0, record.product_id.name)
            sheet.write(1, 1, record.product_id.default_code)
            sheet.write(1, 2, record.product_qty)

            sheet.write(4, 0, _('Reference'), bold_format)
            sheet.write(4, 1, _('Product'), bold_format)
            sheet.write(4, 2, _('Quantity'), bold_format)
            sheet.write(4, 3, _('Percent'), bold_format)
            sheet.write(4, 4, _('Price'), bold_format)
            sheet.write(4, 5, _('Valuation'), bold_format)

            y = 5
            for line in record.bom_quants_total_ids:
                z = y + 1
                sheet.write(y, 0, line.bom_line_id.product_id.default_code)
                sheet.write(y, 1, line.bom_line_id.product_id.name)
                sheet.write(y, 2, line.total_qty)
                sheet.write_formula(y, 3, ('=C%s * C2' % (z)), percent_format)
                sheet.write(y, 4, line.bom_line_id.product_id.standard_price)
                sheet.write_formula(y, 5, ('=E%s * C%s' % (z, z)))
                y += 1

            sheet.write(4, 9, _('Shift Data'), bold_format)
            sheet.write(5, 9, _('Date Start'), bold_format)
            sheet.write(5, 10, record.shift_start_date, datetime_format)
            sheet.write(6, 9, _('Date End'), bold_format)
            sheet.write(6, 10, record.shift_end_date, datetime_format)
            sheet.write(7, 9, _('Notes'), bold_format)
            sheet.write(7, 10, record.notes)

            sheet.write(5, 11, _('Shift Total Time'), bold_format)
            sheet.write(5, 12, '{0:02.0f}:{1:02.0f}'.format(*divmod(record.shift_total_time * 60, 60)))
            sheet.write(6, 11, _('Shift Break Time'), bold_format)
            sheet.write(6, 12, '{0:02.0f}:{1:02.0f}'.format(*divmod(record.shift_break_time * 60, 60)))
            sheet.write(7, 11, _('Shift Stop Time'), bold_format)
            sheet.write(7, 12, '{0:02.0f}:{1:02.0f}'.format(*divmod(record.shift_stop_time * 60, 60)))

            # Set columns widths
            sheet.set_column('A:F', 15)
            sheet.set_column('J:M', 15)
