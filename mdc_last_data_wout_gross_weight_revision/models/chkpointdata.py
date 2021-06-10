import datetime as dt
import logging
from odoo import api, fields, models, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class DataWOut(models.Model):
    _inherit = 'mdc.data_wout'

    old_gross_weight = fields.Float(
        'Gross Weight before revision',
        readonly=True,
        default=0)
    revised_gross_weight_dt = fields.Datetime(
        'Gross Weight review datetime')

    def _last_data_wout_gross_weight_revision(self):
        """
            Review gross weight of last wout:
            modify the gross weight of the last wout of each employee
            with the gross weight calculated from the net weight
            multiplied by the yield percentage of that day for that employee
        :return:
        """
        IrConfParam = self.env['ir.config_parameter'].sudo()
        next_datetime_cron = IrConfParam.get_param(
            'last_data_wout_gross_weight_revision'
            '.last_data_wout_gross_weight_rev_cron')
        if fields.Datetime.to_string(dt.datetime.now()) < next_datetime_cron:
            return

        d = next_datetime_cron[0:10]
        dt_from = d + " 00:00:00"
        dt_to = d + " 23:59:59"

        try:
            # firstly we update if there is previous gross weight revision
            num_reg = 0
            wouts = self.search(
                [('create_datetime', '>=', dt_from),
                 ('create_datetime', '<=', dt_to),
                 ('wout_categ_id.code', '=', 'P'),
                 ('wout_shared_id', '=', False),
                 ('old_gross_weight', '!=', 0)])
            for w in wouts:
                w.write({
                    'gross_weight': w.old_gross_weight,
                    'old_gross_weight': None,
                    'revised_gross_weight_dt': dt.datetime.now()
                })
                num_reg += 1
                _logger.info(
                    '[mdc.data_wout] delete revised_gross_weight of %s - %s (id %s)'
                    % (d, w.employee_id.name, w.id))
            _logger.info(
                '[mdc.data_wout] zero updated %d regs in gross_weight revision'
                % num_reg)

            # now find group of line+lot+employee
            num_reg = 0
            wouts = self.read_group(
                domain=[('create_datetime', '>=', dt_from),
                        ('create_datetime', '<=', dt_to),
                        ('wout_categ_id.code', '=', 'P'),
                        ('wout_shared_id', '=', False)]
                , fields=['employee_id', 'line_id', 'lot_id',
                          'gross_weight', 'weight', 'tare']
                , groupby=['employee_id', 'line_id', 'lot_id']
                , orderby='employee_id, line_id, lot_id'
                , lazy=False
            )
            if wouts:
                for w in wouts:
                    if w['__count'] <= 1:
                        continue
                    last_emp_out = self.search(
                        [('create_datetime', '>=', dt_from),
                         ('create_datetime', '<=', dt_to),
                         ('wout_categ_id.code', '=', 'P'),
                         ('wout_shared_id', '=', False),
                         ('employee_id', '=', w['employee_id'][0])]
                        , order='create_datetime desc', limit=1)

                    #if this lot is not the employee last lot of the day
                    if not last_emp_out \
                            or w['line_id'][0] != last_emp_out.line_id.id \
                            or w['lot_id'][0] != last_emp_out.lot_id.id:
                        continue
                    #calculate new_gross_weight = net_weight * emp_yield
                    tot_gross_weight = w['gross_weight'] - last_emp_out.gross_weight
                    tot_weight = w['weight'] - last_emp_out.weight
                    tot_tare = w['tare'] - last_emp_out.tare
                    tot_net_weight = tot_weight - tot_tare
                    if tot_net_weight <= 0.0 or tot_gross_weight <= 0.0:
                        continue
                    emp_yield = tot_gross_weight / tot_net_weight
                    net_weight = last_emp_out.weight - last_emp_out.tare
                    new_gross_weight = net_weight * emp_yield
                    if new_gross_weight <= 0.0:
                        new_gross_weight = 0.0
                    old_gross_weight = last_emp_out.gross_weight
                    if new_gross_weight < old_gross_weight:
                        last_emp_out.write({
                            'gross_weight': new_gross_weight,
                            'old_gross_weight': old_gross_weight,
                            'revised_gross_weight_dt': dt.datetime.now()
                        })
                        num_reg += 1
                        _logger.info(
                            '[mdc.data_wout] revised_gross_weight of %s - %s '
                            '(id %s) from %f to %f'
                            % (d, last_emp_out.employee_id.name
                               , last_emp_out.id, old_gross_weight
                               , new_gross_weight))
            _logger.info(
                '[mdc.data_wout] updated %d regs in gross_weight revision'
                % num_reg)
            # update next execution date
            next_datetime_cron = dt.datetime.strptime(
                next_datetime_cron, "%Y-%m-%d %H:%M:%S")
            next_datetime_cron = next_datetime_cron + dt.timedelta(days=1)
            IrConfParam.set_param(
                'last_data_wout_gross_weight_revision'
                '.last_data_wout_gross_weight_rev_cron',
                next_datetime_cron)
        except UserError as e:
            _logger.error(
                '[mdc.data_wout] _last_data_wout_gross_weight_revision: %s'
                % e)
