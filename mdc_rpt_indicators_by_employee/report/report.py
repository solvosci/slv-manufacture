# -*- coding: utf-8 -*-

from odoo import api, models, fields, tools, _


class RptIndicatorsByEmployee(models.Model):
    """
    View-mode model that ists data captured at checkpoints (data_win & data_wout) in order to be filtered by dates and exported to Excel
    """
    _name = 'mdc.rpt_indicators_by_employee'
    _description = 'Indicators by Employee Report'
    _order = 'employee_code asc, create_date asc'
    _auto = False

    create_date = fields.Date('Date', readonly=True)
    employee_code = fields.Char('Employee Code', readonly=True)
    employee_name = fields.Char('Employee Name', readonly=True)
    shift_code = fields.Char('Shift Code', readonly=True)
    line_code = fields.Char('Line Code', readonly=True)
    gross_weight_reference = fields.Float('Gross Reference', readonly=True, group_operator='sum')
    gross_weight = fields.Float('Gross', readonly=True, group_operator='sum')
    ind_backs = fields.Float('IND Backs', readonly=True)
    ind_mo = fields.Float('IND MO', readonly=True)
    ind_crumbs = fields.Float('IND Crumbs', readonly=True)
    ind_quality = fields.Float('IND Quality', readonly=True)
    ind_cleaning = fields.Float('IND Cleaning', readonly=True)

    def init(self):
        tools.drop_view_if_exists(self._cr, self._table)
        self._cr.execute("""
                CREATE view %s as 
                    SELECT MIN(datagrup.id) id, datagrup.create_date, 
                        datagrup.employee_code, datagrup.employee_name, datagrup.shift_code, datagrup.line_code, 
                        sum(datagrup.gross_weight_reference) gross_weight_reference, sum(datagrup.gross_weight) gross_weight,
                        case when sum(datagrup.gross_weight_reference)=0 then 0 else sum(datagrup.ind_backs*datagrup.gross_weight_reference)/sum(datagrup.gross_weight_reference) end ind_backs,
                        case when sum(datagrup.gross_weight_reference)=0 then 0 else sum(datagrup.ind_mo*datagrup.gross_weight_reference)/sum(datagrup.gross_weight_reference) end ind_mo,
                        case when sum(datagrup.gross_weight_reference)=0 then 0 else sum(datagrup.ind_crumbs*datagrup.gross_weight_reference)/sum(datagrup.gross_weight_reference) end ind_crumbs,
                        case when sum(datagrup.gross_weight_reference)=0 then 0 else sum(datagrup.ind_quality*datagrup.gross_weight_reference)/sum(datagrup.gross_weight_reference) end ind_quality,
                        case when sum(datagrup.gross_weight_reference)=0 then 0 else sum(datagrup.ind_cleaning*datagrup.gross_weight_reference)/sum(datagrup.gross_weight_reference) end ind_cleaning 
                    FROM (
                        SELECT mdcdata.id, mdcdata.create_date, 
                            mdcdata.employee_code, mdcdata.employee_name, mdcdata.shift_code, mdcdata.line_code, mdcdata.lot_id, 
                            mdcdata.gross_weight_reference, mdcdata.gross_weight,
                            case when coalesce(mdcdata.std_yield_product,0)* mdcdata.gross_weight_reference = 0 then 0 else ((mdcdata.product_weight / mdcdata.gross_weight_reference) / mdcdata.std_yield_product/ 1.15) * 100 * 100 end as ind_backs,
                            case when coalesce(mdcdata.total_hours,0)* mdcdata.gross_weight_reference = 0 then 0 else (mdcdata.std_speed / (mdcdata.total_hours * 60 / mdcdata.gross_weight_reference) / 1.15) * 100 end as ind_mo,
                            case when coalesce(mdcdata.std_yield_sp1,0)* mdcdata.gross_weight_reference = 0 then 0 else ((mdcdata.sp1_weight / mdcdata.gross_weight_reference) / mdcdata.std_yield_sp1 / 1.15) * 100 end as ind_crumbs,
                            case when (mdcdata.product_weight + mdcdata.shared_product_weight) = 0 then 0 else mdcdata.quality_weight/(mdcdata.product_weight + mdcdata.shared_product_weight/2) end as ind_quality,
                            case when coalesce(mdcdata.std_yield_product,0)* coalesce(mdcdata.total_hours,0)* mdcdata.gross_weight_reference * (mdcdata.product_weight + mdcdata.shared_product_weight) = 0 then 0 else
                            (0.6 *  ((mdcdata.product_weight / mdcdata.gross_weight_reference) / mdcdata.std_yield_product/ 1.15) * 100 * 100) 
                            + (0.3 * (mdcdata.std_speed / (mdcdata.total_hours * 60 / mdcdata.gross_weight_reference) / 1.15) * 100) 
                            + (0.1 * mdcdata.quality_weight/(mdcdata.product_weight + mdcdata.shared_product_weight/2)) end as ind_cleaning 
                            FROM (
                                SELECT woutdata.id, woutdata.create_date, 
                                    emp.employee_code, emp.name as employee_name, line.line_code, shift.shift_code, woutdata.lot_id, 
                                    case when (lot.finished and (lot.weight > 0)) then woutdata.gross_weight/(lot.total_gross_weight/lot.weight) when (1-coalesce(lot.std_loss,0)/100) = 0 then 999999 else woutdata.gross_weight /(1-coalesce(lot.std_loss,0)/100) end as gross_weight_reference,
                                    woutdata.gross_weight, woutdata.product_weight, woutdata.sp1_weight, 
                                    case when (1-coalesce(lot.std_loss,0)/100) = 0 then 999999 else woutdata.shared_gross_weight /(1-coalesce(lot.std_loss,0)/100) end as shared_gross_weight_reference,
                                    woutdata.shared_gross_weight, woutdata.shared_product_weight, woutdata.shared_sp1_weight,
                                    case when (woutdata.product_weight + woutdata.shared_product_weight) = 0 then 0 else woutdata.quality_weight/(woutdata.product_weight + woutdata.shared_product_weight/2) end as quality,
                                    woutdata.quality_weight, 
                                    woutdata.product_boxes, woutdata.sp1_boxes, 
                                    lotemp.total_hours, 
                                    lot.std_yield_product, lot.std_speed, lot.std_yield_sp1, lot.std_loss, lot.finished as lot_finished, 
                                    case when (lot.finished and (lot.weight > 0)) then lot.total_gross_weight/lot.weight else 0 end as coef_weight_lot
                                    FROM (
                                        SELECT
                                            MIN(wout.id) as id,
                                            date(wout.create_datetime) as create_date,
                                            wout.lot_id, wout.employee_id, wout.line_id, wout.shift_id, wout.workstation_id,
                                            sum(case when shwout.id is null then wout.gross_weight else 0 end) as gross_weight,
                                            sum(case when shwout.id is null and woutcat.code='P' then wout.weight-wout.tare else 0 end) as product_weight,
                                            sum(case when shwout.id is null and woutcat.code='SP1' then wout.weight-wout.tare else 0 end) as sp1_weight,
                                            sum(case when shwout.id is not null then wout.gross_weight + shwout.gross_weight else 0 end) as shared_gross_weight,
                                            sum(case when shwout.id is not null and woutcat.code='P' then wout.weight-wout.tare + shwout.weight-shwout.tare else 0 end) as shared_product_weight,
                                            sum(case when shwout.id is not null and woutcat.code='SP1' then wout.weight-wout.tare + shwout.weight-shwout.tare else 0 end) as shared_sp1_weight,
                                            sum(case when woutcat.code='P' then qlty.code * (wout.weight-wout.tare) else 0 end) as quality_weight,
                                            sum(case when woutcat.code='P' then 1 else 0 end) as product_boxes,
                                            sum(case when woutcat.code='SP1' then 1 else 0 end) as sp1_boxes
                                        FROM mdc_data_wout wout
                                            LEFT JOIN mdc_wout_categ woutcat ON woutcat.id=wout.wout_categ_id 
                                            LEFT JOIN mdc_quality qlty ON qlty.id=wout.quality_id
                                            LEFT JOIN mdc_data_wout shwout ON shwout.wout_shared_id=wout.id
                                        WHERE 1=1
                                        GROUP BY 
                                            date(wout.create_datetime),
                                            wout.lot_id, wout.employee_id, wout.line_id, wout.shift_id, wout.workstation_id
                                    ) woutdata
                                    LEFT JOIN (SELECT 
                                            date(ws.start_datetime) as start_date,
                                            ws.lot_id, ws.employee_id, ws.shift_id, 
                                            sum(ws.total_hours) as total_hours 
                                        FROM mdc_worksheet ws
                                        WHERE 1=1
                                        GROUP BY date(ws.start_datetime),
                                            ws.lot_id, ws.employee_id, ws.shift_id
                                    ) lotemp ON lotemp.start_date=woutdata.create_date 
                                            and lotemp.lot_id=woutdata.lot_id and lotemp.employee_id=woutdata.employee_id 
                                            and lotemp.shift_id=woutdata.shift_id 
                                    LEFT JOIN mdc_lot lot ON lot.id=woutdata.lot_id
                                    LEFT JOIN hr_employee emp ON emp.id=woutdata.employee_id
                                    LEFT JOIN mdc_shift shift ON shift.id=woutdata.shift_id
                                    LEFT JOIN mdc_line line ON line.id=woutdata.line_id
                                ) mdcdata
                            ) datagrup 
                        GROUP BY datagrup.create_date, datagrup.employee_code, datagrup.employee_name, datagrup.shift_code, datagrup.line_code

            """ % self._table)

    # --------------- Calculate Grouped Values with Weighted average or complicated dropued formulas
    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None,
                   orderby=False, lazy=True):
        res = super(RptIndicatorsByEmployee, self).read_group(domain, fields, groupby,
                                                       offset=offset, limit=limit, orderby=orderby, lazy=lazy)
        group_fields = ['ind_backs', 'ind_mo', 'ind_crumbs', 'ind_quality', 'ind_cleaning']
        if any([x in fields for x in group_fields]) :
            for line in res:
                if '__domain' in line:
                    ind_backs_weight = 0
                    ind_mo_weight = 0
                    ind_crumbs_weight = 0
                    ind_quality_weight = 0
                    ind_cleaning_weight = 0
                    total_weight = 0
                    lines = self.search(line['__domain'])
                    for line_item in lines:
                        ind_backs_weight += line_item.ind_backs * (line_item.gross_weight_reference)
                        ind_mo_weight += line_item.ind_mo * (line_item.gross_weight_reference)
                        ind_crumbs_weight += line_item.ind_crumbs * (line_item.gross_weight_reference)
                        ind_quality_weight += line_item.ind_quality * (line_item.gross_weight_reference)
                        ind_cleaning_weight += line_item.ind_cleaning * (line_item.gross_weight_reference)
                        total_weight += line_item.gross_weight_reference
                    if total_weight > 0:
                        line['ind_backs'] = ind_backs_weight / total_weight
                        line['ind_mo'] = ind_mo_weight / total_weight
                        line['ind_crumbs'] = ind_crumbs_weight / total_weight
                        line['ind_quality'] = ind_quality_weight / total_weight
                        line['ind_cleaning'] = ind_cleaning_weight / total_weight
        return res
