# © 2025 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html
from odoo import models, _


class MdcWeightXlsxReport(models.AbstractModel):
    _name = 'report.mdc_weight_mgmt_xlsx_report.mdc_weight'
    _inherit = 'report.report_xlsx.abstract'
    _description = "XLSX model report"

    def format_time(self,float_time):
        hours, minutes = divmod(int(float_time * 60), 60)
        return f"{hours:02d}:{minutes:02d}"

    def generate_xlsx_report(self, workbook, data, weight_records):
        worksheet = workbook.add_worksheet('Weight Report')
        worksheet.set_column('A:ZZ', 15)
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#D9E1F2',
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'text_wrap': True,
        })
        text_format = workbook.add_format({
            'text_wrap': True,
            'border': 1,
            'align': 'center',
            'valign': 'vcenter'
        })
        decimal_format = workbook.add_format({
            'num_format': '0.00',
            'border': 1,
            'align': 'center',
            'valign': 'vcenter'
        })
        integer_format = workbook.add_format({
            'num_format': '0',
            'border': 1,
            'align': 'center',
            'valign': 'vcenter'
        })

        row = 1
        equipments = weight_records.mdc_weight_record_ids.mapped('equipment_id')
        for equipment in equipments:
            lines = weight_records.mdc_weight_record_ids.filtered(lambda r: r.equipment_id.id == equipment.id)
            products = lines.mapped('product_id')

            worksheet.write(f'A{row}', _('Date:'), header_format)
            worksheet.write(f'B{row}', f"{weight_records.date_from.strftime(_('%d/%m/%Y')) } - {weight_records.date_to.strftime(_('%d/%m/%Y')) }", text_format)
            worksheet.write(f'D{row}', _('Shift:'), header_format)
            shift_time = f"{weight_records.shift_id.name}: {self.format_time(weight_records.shift_id.hour_from)} - {self.format_time(weight_records.shift_id.hour_to)}"
            worksheet.write(f'E{row}', shift_time, text_format)
            worksheet.write(f'G{row}', _('Line:'), header_format)
            worksheet.write(f'H{row}', weight_records.equipment_id.name if weight_records.equipment_id else _("No selected"), text_format)
            worksheet.write(f'J{row}', _('Product:'), header_format)
            worksheet.write(f'K{row}', weight_records.product_id.name if weight_records.product_id else _("No selected"), text_format)
            row += 1

            worksheet.write(f'A{row}', _('Product'), header_format)
            worksheet.write(f'B{row}', _('Nominal Weight'), header_format)
            worksheet.write(f'C{row}', _('Declared Weight'), header_format)
            worksheet.write(f'D{row}', _('Start'), header_format)
            worksheet.write(f'E{row}', _('End'), header_format)
            worksheet.write(f'F{row}', _('Period (min)'), header_format)
            worksheet.write(f'G{row}', _('Total Units'), header_format)
            worksheet.write(f'H{row}', _('Units/min'), header_format)
            worksheet.write(f'I{row}', _('Accepted'), header_format)
            worksheet.write(f'J{row}', _('Accepted (%)'), header_format)
            worksheet.write(f'K{row}', _('Total Acc. Weight'), header_format)
            worksheet.write(f'L{row}', _('Total Acc. Declared'), header_format)
            worksheet.write(f'M{row}', _('Avg Accepted'), header_format)
            worksheet.write(f'N{row}', _('Overweight (%)'), header_format)
            worksheet.write(f'O{row}', _('Overweight'), header_format)
            worksheet.write(f'P{row}', _('Underweight'), header_format)
            worksheet.write(f'Q{row}', _('Total Rejected'), header_format)
            worksheet.write(f'R{row}', _('Rejected (%)'), header_format)
            row += 1

            total_equipment_period_min = 0
            total_equipment_unit_totals = 0
            total_equipment_unit_x_min_avg = 0
            total_equipment_unit_ok = 0
            total_equipment_unit_ok_pct_avg = 0
            total_equipment_weight_ok_tot_qty = 0
            total_equipment_weight_ok_dec_qty = 0
            total_equipment_weight_ok_avg_qty = 0
            total_equipment_exceed_pct_avg = 0
            total_equipment_unit_reject_exceed = 0
            total_equipment_unit_reject_low = 0
            total_equipment_unit_reject_total = 0
            total_equipment_unit_reject_pct_avg = 0

            for product in products:
                products_filtered = sorted(weight_records.mdc_weight_record_ids.filtered(lambda r: r.product_id.id == product.id and r.equipment_id.id == equipment.id), key=lambda r: r.start)
                total_period_min = 0
                total_unit_totals = 0
                total_unit_x_min_avg = 0
                total_unit_ok = 0
                total_unit_ok_pct_avg = 0
                total_weight_ok_tot_qty = 0
                total_weight_ok_dec_qty = 0
                total_weight_ok_avg_qty = 0
                total_exceed_pct_avg = 0
                total_unit_reject_exceed = 0
                total_unit_reject_low = 0
                total_unit_reject_total = 0
                total_unit_reject_pct_avg = 0

                for product_filtered in products_filtered:
                    worksheet.write(row, 0, product_filtered.product_id.name, text_format)
                    worksheet.write(row, 1, product_filtered.weight_nom_qty, text_format)
                    worksheet.write(row, 2, product_filtered.weight_dec_qty or '', text_format)
                    worksheet.write(row, 3, product_filtered.start.strftime('%H:%M'), text_format)
                    worksheet.write(row, 4, product_filtered.end.strftime('%H:%M'), text_format)
                    worksheet.write(row, 5, product_filtered.period_min, integer_format)
                    worksheet.write(row, 6, product_filtered.unit_total, text_format)
                    worksheet.write(row, 7, product_filtered.unit_x_min, decimal_format)
                    worksheet.write(row, 8, product_filtered.unit_ok, text_format)
                    worksheet.write(row, 9, product_filtered.unit_ok_pct, decimal_format)
                    worksheet.write(row, 10, product_filtered.weight_ok_tot_qty, text_format)
                    worksheet.write(row, 11, product_filtered.weight_ok_dec_qty or '', text_format)
                    worksheet.write(row, 12, product_filtered.weight_ok_avg_qty, text_format)
                    worksheet.write(row, 13, product_filtered.exceed_pct, decimal_format)
                    worksheet.write(row, 14, product_filtered.unit_reject_exceed or '', text_format)
                    worksheet.write(row, 15, product_filtered.unit_reject_low or '', text_format)
                    worksheet.write(row, 16, product_filtered.unit_reject_total, text_format)
                    worksheet.write(row, 17, product_filtered.unit_reject_pct, decimal_format)
                    row += 1

                total_period_min = weight_records.sum_total(products_filtered, 'period_min')
                total_unit_totals = weight_records.sum_total(products_filtered, 'unit_total')
                total_unit_ok = weight_records.sum_total(products_filtered, 'unit_ok')
                total_weight_ok_tot_qty = weight_records.sum_total(products_filtered, 'weight_ok_tot_qty')
                total_weight_ok_dec_qty = weight_records.sum_total(products_filtered, 'weight_ok_dec_qty')
                total_unit_reject_exceed = weight_records.sum_total(products_filtered, 'unit_reject_exceed')
                total_unit_reject_low = weight_records.sum_total(products_filtered, 'unit_reject_low')
                total_unit_reject_total = weight_records.sum_total(products_filtered, 'unit_reject_total')
                total_unit_x_min_avg = weight_records.total_avg(total_unit_ok, total_period_min)
                total_weight_ok_avg_qty = weight_records.total_avg(total_weight_ok_tot_qty, total_unit_ok)*1000
                total_unit_ok_pct_avg = weight_records.total_pct_avg(total_unit_ok, total_unit_totals)
                total_exceed_pct_avg = weight_records.total_pct_avg((total_weight_ok_avg_qty - product_filtered.weight_nom_qty),product_filtered.weight_nom_qty)
                if total_unit_reject_total:
                    total_unit_reject_pct_avg = weight_records.total_pct_avg(total_unit_reject_total, total_unit_totals)

                worksheet.write(row, 0, product.name, header_format)
                worksheet.write(row, 5, total_period_min, integer_format)
                worksheet.write(row, 6, total_unit_totals, text_format)
                worksheet.write(row, 7, total_unit_x_min_avg, decimal_format)
                worksheet.write(row, 8, total_unit_ok, text_format)
                worksheet.write(row, 9, total_unit_ok_pct_avg, decimal_format)
                worksheet.write(row, 10, total_weight_ok_tot_qty, text_format)
                worksheet.write(row, 11, total_weight_ok_dec_qty, text_format)
                worksheet.write(row, 12, total_weight_ok_avg_qty, decimal_format)
                worksheet.write(row, 13, total_exceed_pct_avg, decimal_format)
                worksheet.write(row, 14, total_unit_reject_exceed, text_format)
                worksheet.write(row, 15, total_unit_reject_low, text_format)
                worksheet.write(row, 16, total_unit_reject_total, text_format)
                worksheet.write(row, 17, total_unit_reject_pct_avg, decimal_format)
                row += 1

            total_weight_nom_qty = weight_records.total_weight_nom(lines)
            total_equipment_period_min = weight_records.sum_total(lines, 'period_min')
            total_equipment_unit_totals = weight_records.sum_total(lines, 'unit_total')
            total_equipment_unit_ok = weight_records.sum_total(lines, 'unit_ok')
            total_equipment_weight_ok_tot_qty = weight_records.sum_total(lines, 'weight_ok_tot_qty')
            total_equipment_weight_ok_dec_qty = weight_records.sum_total(lines, 'weight_ok_dec_qty')
            total_equipment_unit_reject_exceed = weight_records.sum_total(lines, 'unit_reject_exceed')
            total_equipment_unit_reject_low = weight_records.sum_total(lines, 'unit_reject_low')
            total_equipment_unit_reject_total = weight_records.sum_total(lines, 'unit_reject_total')
            total_equipment_unit_x_min_avg = weight_records.total_avg(total_equipment_unit_totals, total_equipment_period_min)
            total_equipment_weight_ok_avg_qty = weight_records.total_avg(total_equipment_weight_ok_tot_qty, total_equipment_unit_ok) * 1000
            total_equipment_unit_ok_pct_avg = weight_records.total_pct_avg(total_equipment_unit_ok, total_equipment_unit_totals)
            total_equipment_exceed_pct_avg = weight_records.total_pct_avg((total_equipment_weight_ok_avg_qty - total_weight_nom_qty),total_weight_nom_qty)
            if total_equipment_unit_reject_total:
                total_equipment_unit_reject_pct_avg = weight_records.total_pct_avg(total_equipment_unit_reject_total, total_equipment_unit_totals)

            worksheet.write(row, 0, equipment.name, header_format)
            worksheet.write(row, 1, total_weight_nom_qty, integer_format)
            worksheet.write(row, 5, total_equipment_period_min, integer_format)
            worksheet.write(row, 6, total_equipment_unit_totals, text_format)
            worksheet.write(row, 7, total_equipment_unit_x_min_avg, decimal_format)
            worksheet.write(row, 8, total_equipment_unit_ok, text_format)
            worksheet.write(row, 9, total_equipment_unit_ok_pct_avg, decimal_format)
            worksheet.write(row, 10, total_equipment_weight_ok_tot_qty, text_format)
            worksheet.write(row, 11, total_equipment_weight_ok_dec_qty, text_format)
            worksheet.write(row, 12, total_equipment_weight_ok_avg_qty, decimal_format)
            worksheet.write(row, 13, total_equipment_exceed_pct_avg, decimal_format)
            worksheet.write(row, 14, total_equipment_unit_reject_exceed, text_format)
            worksheet.write(row, 15, total_equipment_unit_reject_low, text_format)
            worksheet.write(row, 16, total_equipment_unit_reject_total, text_format)
            worksheet.write(row, 17, total_equipment_unit_reject_pct_avg, decimal_format)
            row += 3
