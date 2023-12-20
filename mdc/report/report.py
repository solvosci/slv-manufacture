# -*- coding: utf-8 -*-

from odoo import api, models, fields, tools, _

class RptStageManufacturing(models.Model):
    """
    View-mode model that ists data captured at checkpoints (data_win & data_wout) in order to be filtered by dates and exported to Excel
    """
    _name = 'mdc.rpt_stage_manufacturing'
    _description = 'Stage Manufacturing Report'
    _order = 'lot_name asc, shift_code asc, line_code asc, stage_name asc, employee_name asc'
    _auto = False

    create_date = fields.Date('Date', readonly=True)
    lot_name = fields.Char('MO', readonly=True)
    product_id = fields.Many2one('product.product', 'Product', readonly=True)
    shift_code = fields.Char('Shift Code', readonly=True)
    line_code = fields.Char('Line Code', readonly=True)
    stage_name = fields.Char('Stage Name', readonly=True)
    workstation_name = fields.Char('Workstation Name', readonly=True)
    employee_code = fields.Char('Employee Code', readonly=True)
    employee_name = fields.Char('Employee Name', readonly=True)
    gross_weight = fields.Float('Gross', readonly=True, group_operator='sum')
    product_weight = fields.Float('Backs', readonly=True, group_operator='sum')
    sp1_weight = fields.Float('Crumbs', readonly=True, group_operator='sum')
    sp2_weight = fields.Float('Crumbs 2', readonly=True, group_operator='sum')
    quality_weight = fields.Float('Quality', readonly=True)
    total_hours = fields.Float('Total Hours', readonly=True, group_operator='sum')

    def init(self):
        tools.drop_view_if_exists(self._cr, self._table)
        self._cr.execute("""
                CREATE view %s as 
                SELECT woutdata.id, woutdata.create_date, lot.name AS lot_name,
                    lot.product_id, shift.shift_code, line.line_code, stage.name AS stage_name,
                    wst.name AS workstation_name, emp.employee_code, emp.name AS employee_name,
                    woutdata.gross_weight, woutdata.product_weight, woutdata.sp1_weight, woutdata.sp2_weight,
                    woutdata.quality_weight,
                    lotemp.total_hours
                    FROM (
                        SELECT
                            MIN(wout.id) as id,
                            date(wout.create_datetime) as create_date,
                            wout.lot_id,
                            wout.shift_id,
                            wout.line_id,
                            wout.stage_id,
                            wout.workstation_id,
                            wout.employee_id,
                            sum(wout.gross_weight) as gross_weight,
                            sum(case when woutcat.code='P' then wout.weight-wout.tare else 0 end) as product_weight,
                            sum(case when woutcat.code='SP1' then wout.weight-wout.tare else 0 end) as sp1_weight,
                            sum(case when woutcat.code='SP2' then wout.weight-wout.tare else 0 end) as sp2_weight,
                            sum(case when woutcat.code='P' then qlty.code * (wout.weight-wout.tare) else 0 end) as quality_weight
                        FROM mdc_data_wout wout
                            LEFT JOIN mdc_wout_categ woutcat ON woutcat.id=wout.wout_categ_id 
                            LEFT JOIN mdc_quality qlty ON qlty.id=wout.quality_id
                        WHERE 1=1
                        GROUP BY 
                            date(wout.create_datetime),
                            wout.lot_id, wout.shift_id, wout.line_id, wout.stage_id, wout.workstation_id, wout.employee_id
                    ) as woutdata 		
                    LEFT JOIN (
                        SELECT 
                        date(ws.start_datetime) as start_date,
                        ws.lot_id, ws.employee_id, ws.shift_id,
                        wst.stage_id,
                        sum(ws.total_hours) as total_hours
                        FROM mdc_worksheet ws
                        LEFT JOIN mdc_workstation wst ON wst.id=ws.workstation_id
                        WHERE 1=1
                        GROUP BY date(ws.start_datetime),
                        ws.lot_id, ws.employee_id, ws.shift_id, wst.stage_id
                    ) as lotemp ON 
                        lotemp.start_date = woutdata.create_date AND lotemp.lot_id = woutdata.lot_id AND
                        lotemp.employee_id = woutdata.employee_id AND lotemp.shift_id=woutdata.shift_id AND
                        lotemp.stage_id = woutdata.stage_id
                    LEFT JOIN mdc_lot lot ON lot.id=woutdata.lot_id
                    LEFT JOIN mdc_shift shift ON shift.id=woutdata.shift_id
                    LEFT JOIN mdc_line line ON line.id=woutdata.line_id
                    LEFT JOIN mdc_stage stage ON stage.id=woutdata.stage_id
                    LEFT JOIN mdc_workstation wst ON wst.id=woutdata.workstation_id
                    LEFT JOIN hr_employee emp ON emp.id=woutdata.employee_id
            """ % self._table)

    # --------------- Calculate Grouped Values with Weighted average or complicated dropued formulas
    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None,
                   orderby=False, lazy=True):
        res = super(RptStageManufacturing, self).read_group(domain, fields, groupby,
                                                       offset=offset, limit=limit, orderby=orderby, lazy=lazy)
        # we don´t calculate ind_ fields because they aren´t in tree view
        # group_fields = ['quality', 'ind_backs', 'ind_mo', 'ind_crumbs', 'ind_quality','ind_cleaning']
        group_fields = ['quality']
        if any([x in fields for x in group_fields]):
            for line in res:
                if '__domain' in line:
                    quality_weight = 0
                    total_weight = 0
                    lines = self.search(line['__domain'])
                    for line_item in lines:
                        quality_weight += line_item.quality * (line_item.product_weight + line_item.shared_product_weight / 2)
                        total_weight += line_item.product_weight + line_item.shared_product_weight / 2
                    if total_weight > 0:
                        line['quality'] = quality_weight / total_weight
        return res


class RptLineManufacturing(models.Model):
    """
    View-mode model that ists data captured at checkpoints (data_win & data_wout) in order to be filtered by dates and exported to Excel
    """
    _name = 'mdc.rpt_line_manufacturing'
    _description = 'Line Manufacturing Report'
    _order = 'lot_name asc, line_code asc'
    _auto = False

    create_date = fields.Date('Date', readonly=True)
    lot_name = fields.Char('MO', readonly=True)
    product_id = fields.Many2one('product.product', 'Product', readonly=True)
    line_code = fields.Char('Line Code')
    workstation_name = fields.Char('Workstation Name', readonly=True)
    final_gross_weight = fields.Float('Final Gross Weight', readonly=True)
    product_weight = fields.Float('Backs', readonly=True, group_operator='sum')
    sp1_weight = fields.Float('Crumbs', readonly=True, group_operator='sum')
    sp2_weight = fields.Float('Crumbs 2', readonly=True, group_operator='sum')
    quality_weight = fields.Float('Quality', readonly=True, group_operator='sum')
    total_hours = fields.Float('Total Hours', readonly=True, group_operator='sum')

    def init(self):
        tools.drop_view_if_exists(self._cr, self._table)
        self._cr.execute("""
            CREATE view %s as 
                SELECT woutdata.id, woutdata.create_date, lot.name AS lot_name,
                    lot.product_id, line.line_code,
                    wst.name AS workstation_name,
                    woutdata.final_gross_weight, woutdata.product_weight, woutdata.sp1_weight, woutdata.sp2_weight,
                    woutdata.quality_weight,
                    lotemp.total_hours
                    FROM (
                        SELECT
                            MIN(wout.id) as id,
                            date(wout.create_datetime) as create_date,
                            wout.lot_id,
                            wout.line_id,
                            wout.workstation_id,
                            sum(wout.final_gross_weight) AS final_gross_weight,
                            sum(case when woutcat.code='P' then wout.weight-wout.tare else 0 end) as product_weight,
                            sum(case when woutcat.code='SP1' then wout.weight-wout.tare else 0 end) as sp1_weight,
                            sum(case when woutcat.code='SP2' then wout.weight-wout.tare else 0 end) as sp2_weight,
                            sum(case when woutcat.code='P' then qlty.code * (wout.weight-wout.tare) else 0 end) as quality_weight
                        FROM mdc_data_wout wout
                            LEFT JOIN mdc_wout_categ woutcat ON woutcat.id=wout.wout_categ_id 
                            LEFT JOIN mdc_quality qlty ON qlty.id=wout.quality_id
                        WHERE final_gross_weight != 0
                        GROUP BY 
                            date(wout.create_datetime),
                            wout.lot_id, wout.line_id, wout.workstation_id, wout.final_gross_weight
                    ) as woutdata 		
                    LEFT JOIN (
                        SELECT 
                        date(ws.start_datetime) as start_date,
                        ws.lot_id,
                        sum(ws.total_hours) as total_hours
                        FROM mdc_worksheet ws
                        LEFT JOIN mdc_workstation wst ON wst.id=ws.workstation_id
                        WHERE 1=1
                        GROUP BY date(ws.start_datetime),
                        ws.lot_id
                    ) as lotemp ON 
                        lotemp.start_date = woutdata.create_date AND lotemp.lot_id = woutdata.lot_id
                    LEFT JOIN mdc_lot lot ON lot.id=woutdata.lot_id
                    LEFT JOIN mdc_line line ON line.id=woutdata.line_id
                    LEFT JOIN mdc_workstation wst ON wst.id=woutdata.workstation_id
        """ % self._table)

    # --------------- Calculate Grouped Values with Weighted average or complicated dropued formulas
    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None,
        orderby=False, lazy=True):
        res = super(RptLineManufacturing, self).read_group(domain, fields, groupby,
            offset=offset, limit=limit, orderby=orderby, lazy=lazy)
        # we don´t calculate ind_ fields because they aren´t in tree view
        # group_fields = ['quality', 'ind_backs', 'ind_mo', 'ind_crumbs', 'ind_quality','ind_cleaning']
        group_fields = ['quality']
        if any([x in fields for x in group_fields]):
            for line in res:
                if '__domain' in line:
                    quality_weight = 0
                    total_weight = 0
                    lines = self.search(line['__domain'])
                    for line_item in lines:
                        quality_weight += line_item.quality * (line_item.product_weight + line_item.shared_product_weight / 2)
                        total_weight += line_item.product_weight + line_item.shared_product_weight / 2
                    if total_weight > 0:
                        line['quality'] = quality_weight / total_weight
        return res


class RptEmployeeYield(models.Model):
    """
    View-mode model that ists data captured at checkpoints (data_win & data_wout) in order to be filtered by dates and exported to Excel
    """
    _name = 'mdc.rpt_employee_yield'
    _description = 'Employee Yield Report'
    _order = 'line_code asc, stage_name asc, employee_name asc'
    _auto = False

    create_date = fields.Date('Date', readonly=True)
    employee_code = fields.Char('Employee Code', readonly=True)
    employee_name = fields.Char('Employee Name', readonly=True)
    shift_code = fields.Char('Shift Code', readonly=True)
    line_code = fields.Char('Line Code', readonly=True)
    stage_name = fields.Char('Stage Name', readonly=True)
    product_id = fields.Many2one('product.product', 'Product', readonly=True)
    gross_weight = fields.Float('Gross', readonly=True, group_operator='sum')
    product_weight = fields.Float('Backs', readonly=True, group_operator='sum')
    sp1_weight = fields.Float('Crumbs', readonly=True, group_operator='sum')
    sp2_weight = fields.Float('Crumbs 2', readonly=True, group_operator='sum')
    quality_weight = fields.Float('Quality', readonly=True)
    total_hours = fields.Float('Total Hours', readonly=True, group_operator='sum')

    def init(self):
        tools.drop_view_if_exists(self._cr, self._table)
        self._cr.execute("""
                CREATE view %s as 
                    SELECT woutdata.id, woutdata.create_date, emp.employee_code, emp.name AS employee_name,
                        shift.shift_code, line.line_code, stage.name AS stage_name, lot.product_id,
                        woutdata.gross_weight, woutdata.product_weight, woutdata.sp1_weight, woutdata.sp2_weight,
                        woutdata.quality_weight,
                        lotemp.total_hours
                    FROM (
                        SELECT
                            MIN(wout.id) as id,
                            date(wout.create_datetime) as create_date,
                            wout.lot_id,
                            wout.shift_id,
                            wout.line_id,
                            wout.stage_id,
                            wout.employee_id,
                            sum(wout.gross_weight) as gross_weight,
                            sum(case when woutcat.code='P' then wout.weight-wout.tare else 0 end) as product_weight,
                            sum(case when woutcat.code='SP1' then wout.weight-wout.tare else 0 end) as sp1_weight,
                            sum(case when woutcat.code='SP2' then wout.weight-wout.tare else 0 end) as sp2_weight,
                            sum(case when woutcat.code='P' then qlty.code * (wout.weight-wout.tare) else 0 end) as quality_weight
                        FROM mdc_data_wout wout
                            LEFT JOIN mdc_wout_categ woutcat ON woutcat.id=wout.wout_categ_id 
                            LEFT JOIN mdc_quality qlty ON qlty.id=wout.quality_id
                        WHERE 1=1
                        GROUP BY 
                            date(wout.create_datetime),
                            wout.lot_id, wout.shift_id, wout.line_id, wout.stage_id, wout.employee_id
                    ) as woutdata 		
                    LEFT JOIN (
                        SELECT 
                        date(ws.start_datetime) as start_date,
                        ws.lot_id, ws.employee_id, ws.shift_id,
                        wst.stage_id,
                        sum(ws.total_hours) as total_hours
                        FROM mdc_worksheet ws
                        LEFT JOIN mdc_workstation wst ON wst.id=ws.workstation_id
                        WHERE 1=1
                        GROUP BY date(ws.start_datetime),
                        ws.lot_id, ws.employee_id, ws.shift_id, wst.stage_id
                    ) as lotemp ON 
                        lotemp.start_date = woutdata.create_date AND lotemp.lot_id = woutdata.lot_id AND
                        lotemp.employee_id = woutdata.employee_id AND lotemp.shift_id=woutdata.shift_id AND
                        lotemp.stage_id = woutdata.stage_id
                    LEFT JOIN mdc_lot lot ON lot.id=woutdata.lot_id
                    LEFT JOIN mdc_shift shift ON shift.id=woutdata.shift_id
                    LEFT JOIN mdc_line line ON line.id=woutdata.line_id
                    LEFT JOIN mdc_stage stage ON stage.id=woutdata.stage_id
                    LEFT JOIN hr_employee emp ON emp.id=woutdata.employee_id
            """ % self._table)

    # --------------- Calculate Grouped Values with Weighted average or complicated dropued formulas
    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None,
        orderby=False, lazy=True):
        res = super(RptEmployeeYield, self).read_group(domain, fields, groupby,
            offset=offset, limit=limit, orderby=orderby, lazy=lazy)
        # we don´t calculate ind_ fields because they aren´t in tree view
        # group_fields = ['quality', 'ind_backs', 'ind_mo', 'ind_crumbs', 'ind_quality','ind_cleaning']
        group_fields = ['quality']
        if any([x in fields for x in group_fields]):
            for line in res:
                if '__domain' in line:
                    quality_weight = 0
                    total_weight = 0
                    lines = self.search(line['__domain'])
                    for line_item in lines:
                        quality_weight += line_item.quality * (line_item.product_weight + line_item.shared_product_weight / 2)
                        total_weight += line_item.product_weight + line_item.shared_product_weight / 2
                    if total_weight > 0:
                        line['quality'] = quality_weight / total_weight
        return res
