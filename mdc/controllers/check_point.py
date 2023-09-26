# -*- coding: utf-8 -*-

import logging
from odoo import http, fields, _
from odoo.exceptions import UserError
from odoo.http import request

from .. import ws_rfid_server


_logger = logging.getLogger(__name__)


class CheckPoint(http.Controller):

    # TODO request parameter should not required
    def _get_cp_user_and_lang_context(self, request):
        cp_user = request.env.ref('mdc.mdc_user_cp')
        # https://stackoverflow.com/questions/42411147/update-context-in-odoo-controller-request-env-context' \
        context = request.env.context.copy()
        context.update({'lang': cp_user.sudo().lang})
        request.env.context = context
        return cp_user

    def _get_client_ip(self):
        remote_ip = request.httprequest.environ.get('HTTP_X_REAL_IP')
        if not remote_ip:
            remote_ip = request.httprequest.environ.get('REMOTE_ADDR')
        return remote_ip

    def _check_client(self, checkpoint, client_ip, simul=False):
        if not simul and checkpoint.allowed_ip and (checkpoint.allowed_ip != client_ip):
            raise UserError(_('The checkpoint %s is not allowed for this address (%s)') % (checkpoint.name, client_ip))

    # Example route
    # TODO remove
    @http.route('/mdc/scales', type='http', auth='none')
    def scales(self):
        res = '''
            <html>
                <head>
                    <script language="JavaScript" src="/mdc/static/src/js/jquery-3.3.1.min.js"></script>
                </head>
                <body>
                    Scale list:
                    <table><tr><td>%s</td></tr></table>
                </body>
            </html>
        '''

        scales = request.env['mdc.scale'].sudo().search([])
        return res % '</td></tr><tr><td>'.join(scales.mapped('name'))

    def get_error_page(self, data):
        data['title'] = 'ERROR - MDC CP'
        data['client_ip'] = self._get_client_ip()
        return request.render('mdc.chkpoint_err', data)

    @http.route('/mdc/cp/list', type='http', auth='none')
    def cp_list(self):
        try:
            cp_user = self._get_cp_user_and_lang_context(request)
            chkpoints = request.env['mdc.chkpoint'].sudo(cp_user).search([], order='order')
            return request.render(
                'mdc.chkpoint_list',
                {'chkpoints': chkpoints}
            )
        except Exception as e:
            return self.get_error_page({
                'error_message': e})

    @http.route("/mdc/cp/win/<int:chkpoint_id>", type='http', auth='none')
    def cp_win(self, chkpoint_id, **kwargs):
        try:
            cp_user = self._get_cp_user_and_lang_context(request)
            ws_session_data = ws_rfid_server.get_session_data(request.env, simul=('rfidsimul' in kwargs))
            chkpoints = request.env['mdc.chkpoint'].sudo(cp_user).browse(chkpoint_id)
            client_ip = self._get_client_ip()
            self._check_client(checkpoint=chkpoints, client_ip=client_ip, simul=ws_session_data['simul'])
            #self._check_client(checkpoint=chkpoints, client_ip=client_ip, simul=False)
            return request.render(
                'mdc.chkpoint_win',
                {'title': chkpoints[0].name, 'chkpoints': chkpoints, 'ws_session_data': ws_session_data,
                 'client_ip': client_ip}
            )
        except Exception as e:
            return self.get_error_page({
                'error_message': e})

    @http.route("/mdc/cp/win/<int:chkpoint_id>/lotactive", type='json', auth='none')
    def cp_win_lotactive(self, chkpoint_id):
        cp_user = self._get_cp_user_and_lang_context(request)
        chkpoints = request.env['mdc.chkpoint'].sudo(cp_user).browse(chkpoint_id)
        data = {
            'ckhpoint_id': chkpoint_id
        }
        try:
            if chkpoints:
                data['lotactive'] = ''
                if chkpoints[0].current_lot_active_id:
                    data['lotactive'] = chkpoints[0].current_lot_active_id.alias_cp
            else:
                raise UserError(_('Checkpoint #%s not found') % chkpoint_id)
        except UserError as e:
            data['err'] = e
        finally:
            return data

    @http.route("/mdc/cp/win/<int:chkpoint_id>/save", type='json', auth='none')
    def cp_win_save(self, chkpoint_id):
        cp_user = self._get_cp_user_and_lang_context(request)
        data_in = dict(request.jsonrequest)
        data_in['chkpoint_id'] = chkpoint_id
        data_out = {
            'ckhpoint_id': chkpoint_id
        }

        try:
            DataWIn = request.env['mdc.data_win'].sudo(cp_user)
            datawin = DataWIn.from_cp_create(data_in)
            data_out['card_code'] = data_in['card_code']
            data_out['data_win_id'] = datawin.id
            data_out['lotactive'] = datawin.lot_id.alias_cp
            data_out['weight'] = '{0:.2f}'.format(datawin.weight)
            data_out['w_uom'] = datawin.w_uom_id.name
        except Exception as e:
            data_out['err'] = e
        finally:
            return data_out

    @http.route("/mdc/cp/wout/<int:chkpoint_id>", type='http', auth='none')
    def cp_wout(self, chkpoint_id, **kwargs):
        try:
            _logger.info("[cp_wout] Page requested for chkpoint_id=%d" % chkpoint_id)
            cp_user = self._get_cp_user_and_lang_context(request)
            ws_session_data = ws_rfid_server.get_session_data(request.env, simul=('rfidsimul' in kwargs))
            chkpoints = request.env['mdc.chkpoint'].sudo(cp_user).browse(chkpoint_id)
            client_ip = self._get_client_ip()
            self._check_client(checkpoint=chkpoints, client_ip=client_ip, simul=ws_session_data['simul'])
            qualities = request.env['mdc.quality'].sudo(cp_user).search([], order='code')
            return request.render(
                'mdc.chkpoint_wout',
                {'title': chkpoints[0].name, 'chkpoints': chkpoints, 'qualities': qualities,
                 'ws_session_data': ws_session_data,
                 'card_categ_P_id': request.env.ref('mdc.mdc_card_categ_P').id,
                 'card_categ_L_id': request.env.ref('mdc.mdc_card_categ_L').id,
                 'card_categ_PC_id': request.env.ref('mdc.mdc_card_categ_PC').id,
                 'client_ip': client_ip
                 }
            )
        except Exception as e:
            return self.get_error_page({
                'error_message': e})

    @http.route("/mdc/cp/wout/<int:chkpoint_id>/save", type='json', auth='none')
    def cp_wout_save(self, chkpoint_id):
        cp_user = self._get_cp_user_and_lang_context(request)
        data_in = dict(request.jsonrequest)
        data_in['chkpoint_id'] = chkpoint_id
        data_out = {
            'ckhpoint_id': chkpoint_id
        }

        try:
            DataWOut = request.env['mdc.data_wout'].sudo(cp_user)
            datawout = DataWOut.from_cp_create(data_in)
            data_out['data_win_id'] = datawout.id
            data_out['lot'] = datawout.lot_id.name
            data_out['weight'] = '{0:.2f}'.format(datawout.weight)
            data_out['w_uom'] = datawout.w_uom_id.name
        except Exception as e:
            data_out['err'] = e
            _logger.error("[cp_wout_save] %s" % e)
        finally:
            return data_out

    @http.route("/mdc/cp/log", type='json', auth='none')
    def cp_log(self):
        cp_user = self._get_cp_user_and_lang_context(request)
        data_in = dict(request.jsonrequest)
        _logger.info('[cp_log] Log saving request with parameters=%s' % data_in)
        data_out = {}
        return data_out

    @http.route('/mdc/cp/cardreg', type='http', auth='none')
    def cp_cardreg(self):
        try:
            cp_user = self._get_cp_user_and_lang_context(request)
            devices = request.env['mdc.rfid_reader'].sudo(cp_user).search([])
            card_categs = request.env['mdc.card_categ'].sudo(cp_user).search([])
            employees = request.env['hr.employee'].sudo(cp_user).search([('operator', '=', True)])
            workstations = request.env['mdc.workstation'].sudo(cp_user).search([])
            ws_session_data = ws_rfid_server.get_session_data(request.env)
            client_ip = self._get_client_ip()
            return request.render(
                'mdc.chkpoint_card_registration',
                {'title': _('Card registration'),
                 'devices': devices, 'card_categs': card_categs, 'employees': employees, 'workstations': workstations,
                 'ws_session_data': ws_session_data, 'client_ip': client_ip}
            )
        except Exception as e:
            return self.get_error_page({
                'error_message': e})

    @http.route('/mdc/cp/cardreg/save', type='json', auth='none')
    def cp_cardreg_save(self):
        cp_user = self._get_cp_user_and_lang_context(request)
        Card = request.env['mdc.card'].sudo(cp_user)
        try:
            card = Card.create({
                'name': request.jsonrequest['card_code'],
                'card_categ_id': request.jsonrequest['card_categ_id'],
                'employee_id': request.jsonrequest['employee_id'],
                'workstation_id': request.jsonrequest['workstation_id'],
            })
            return {
                'card_id': card.id
            }
        except Exception as e:
            return {
                'err': e
            }

    @http.route('/mdc/cp/cardlot', type='http', auth='none')
    def cp_cardlot(self):
        try:
            cp_user = self._get_cp_user_and_lang_context(request)
            devices = request.env['mdc.rfid_reader'].sudo(cp_user).search([])
            lots = request.env['mdc.lot'].sudo(cp_user)\
                .search(['&', ('start_date', '<=', fields.Date.today()),
                         '|', ('end_date', '=', False), ('end_date', '>=', fields.Date.today())])
            ws_session_data = ws_rfid_server.get_session_data(request.env)
            client_ip = self._get_client_ip()
            return request.render(
                'mdc.chkpoint_card_lot_assignment',
                {'title': _('Card lot assignment'), 'devices': devices, 'lots': lots,
                 'ws_session_data': ws_session_data, 'client_ip': client_ip}
            )
        except Exception as e:
            return self.get_error_page({
                'error_message': e})

    @http.route('/mdc/cp/cardlot/save', type='json', auth='none')
    def cp_cardlot_save(self):
        cp_user = self._get_cp_user_and_lang_context(request)
        data_in = dict(request.jsonrequest)
        Card = request.env['mdc.card'].sudo(cp_user)
        try:
            return Card.from_cp_assign_lot(data_in)
        except Exception as e:
            return {
                'err': e
            }

    @http.route('/mdc/cp/carddata/<string:card_code>', type='json', auth='none')
    def cp_carddata(self, card_code):
        try:
            cp_user = self._get_cp_user_and_lang_context(request)
            return request.env['mdc.card'].sudo(cp_user).from_cp_get_card_data(card_code)
        except Exception as e:
            return {
                'card_code': card_code,
                'err': e
            }
