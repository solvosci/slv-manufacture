# © 2022 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html

import json
import logging
from odoo.http import request
from odoo import http, fields, _
from datetime import date, timedelta
import socket
import random
import requests
from lxml import html
import xmlrpc.client
import time

_logger = logging.getLogger(__name__)

class WeightScaleCheckPoint(http.Controller):

    def _get_client_ip(self):
        remote_ip = request.httprequest.environ.get('HTTP_X_REAL_IP')
        if not remote_ip:
            remote_ip = request.httprequest.environ.get('REMOTE_ADDR')
        return remote_ip

    def _get_access(self):
        company_id = request.env.company.search([])[0]
        db = request.env.cr.dbname
        url = http.request.httprequest.host_url + "xmlrpc/common"
        user = company_id.weight_scale_username_id.login
        pwd = company_id.weight_scale_password
        if user and pwd:
            try:
                common = xmlrpc.client.ServerProxy(url)
                request.env.uid = common.login(db, user, pwd)
                pass
            except Exception as e:
                self.get_error_page({'error_message': e})

    def _get_cp_user_and_lang_context(self, request):
        if not request.env.uid:
            self._get_access()
        user_id = request.env['res.users'].sudo().browse(request.env.uid)
        request.env.user = user_id
        cp_user = request.env.ref('fcd_weight_scale_mrp.res_user_fcd_checkpoint_user')
        if user_id:
            context = request.env.context.copy()
            context.update({'lang': cp_user.sudo().lang})
            request.env.context = context
        return cp_user, user_id

    def get_error_page(self, data):
        data['title'] = 'ERROR - WEIGHT SCALE'
        data['client_ip'] = self._get_client_ip()
        return request.render('fcd_weight_scale_mrp.chkpoint_weight', data)

    @http.route('/fcd_weight_scale_mrp/session/authenticate', type='json', auth="none")
    def fcd_weight_scale_mrp_session_authenticate(self, **kwargs):
        company_id = request.env.company.search([])[0]
        db = request.env.cr.dbname
        login = company_id.weight_scale_username_id.login
        password = company_id.weight_scale_password
        request.session.authenticate(db, login, password)

        return json.dumps({'session': request.env['ir.http'].session_info(), 'token': request.session.session_token})

    @http.route('/fcd_weight_scale_mrp/list/', type='http', auth='none')
    def fcd_weight_scale_mrp_list(self, **kwargs):
        try:
            cp_user, user_id = self._get_cp_user_and_lang_context(request)
            chkpoints = request.env['fcd.checkpoint'].with_user(cp_user).search([], order='name')

            return request.render(
                'fcd_weight_scale_mrp.chkpoint_list',
                {
                    'chkpoints': chkpoints,
                    'user_id': user_id,
                })
        except Exception as e:
            return self.get_error_page({
                'error_message': e})

    @http.route("/fcd_weight_scale_mrp/<int:chkpoint_id>", type='http', auth='none')
    def fcd_weight_scale_mrp_scale_view(self, chkpoint_id, **kwargs):
        try:
            cp_user, user_id = self._get_cp_user_and_lang_context(request)
            chkpoint_id = request.env['fcd.checkpoint'].with_user(cp_user).browse(chkpoint_id)
            client_ip = self._get_client_ip()
            if chkpoint_id.allowed_ip == False or chkpoint_id.allowed_ip == client_ip:
                return request.render(
                    'fcd_weight_scale_mrp.chkpoint_weight',
                    {'chkpoint': chkpoint_id,
                    'user_id': user_id,
                    'client_ip': client_ip,
                })
            else:
                return request.render(
                    'fcd_weight_scale_mrp.error_page',
                    {'title': chkpoint_id[0].name,
                    'chkpoints': chkpoint_id,
                    'client_ip': client_ip}
                )

        except Exception as e:
            _logger.warning(e)
            return self.get_error_page({
                'error_message': e})

    @http.route("/fcd_weight_scale_mrp/lotactive", type='json', auth='none')
    def fcd_weight_scale_mrp_lotactive(self, **kwargs):
        cp_user = request.env.ref('fcd_weight_scale_mrp.res_user_fcd_checkpoint_user')
        vals = dict(request.jsonrequest)
        chkpoint_id = request.env['fcd.checkpoint'].with_user(cp_user).browse(int(vals["checkpoint_id"]))
        purchase_order_ids = request.env['purchase.order'].with_user(cp_user).search([])
        purchase_line_ids = purchase_order_ids.order_line.filtered(lambda x: x.fcd_document_line_id.id != False and
        x.fcd_lot_finished is False and
        x.order_id.picking_type_id.warehouse_id == chkpoint_id.warehouse_id)

        try:
            move_ids = []
            for line in purchase_line_ids:
                move_id = False
                if len(line.move_ids) == 1:
                    move_id = line.move_ids
                elif line.move_ids.filtered(lambda x: x.state == 'done'):
                    move_id = line.move_ids.filtered(lambda x: x.state == 'done')[0]
                elif line.move_ids.filtered(lambda x: x.state == 'assigned'):
                    move_id = line.move_ids.filtered(lambda x: x.state == 'assigned')[0]
                if move_id:
                    move_ids.append({
                        "move_id": move_id.id,
                        "lot_name": line.fcd_document_line_id.name,
                        "product_name": move_id.product_id.name,
                        "product_id": move_id.product_id.id,
                        "qty_pending": line.product_qty - line.qty_received,
                        "family_id": move_id.product_id.categ_id.name,
                        "stock_production_lot_name": line.fcd_document_line_id.lot_id.name
                    })
            return json.dumps(move_ids)
        except Exception as e:
            _logger.warning(e)
            return {"error": "Can't get lots, please contact with Administrator"}

    @http.route("/fcd_weight_scale_mrp/productget", type='json', auth='none')
    def fcd_weight_scale_mrp_getproduct(self, **kwargs):
        cp_user = request.env.ref('fcd_weight_scale_mrp.res_user_fcd_checkpoint_user')
        vals = dict(request.jsonrequest)
        products_return = []
        product_ids = request.env['product.product'].with_user(cp_user).search([('categ_id.name', '=', vals['jsonSend']['family_id']), ('sale_ok', '=', True)], order="name")
        for record in product_ids:
            products_return.append({
                "product_name": record.name,
                "product_id": record.id,
                "type_box": record.stock_secondary_uom_id.id,
            })
        return json.dumps(products_return)

    @http.route("/fcd_weight_scale_mrp/familyget", type='json', auth='none')
    def fcd_weight_scale_mrp_getfamily(self, **kwargs):
        cp_user = request.env.ref('fcd_weight_scale_mrp.res_user_fcd_checkpoint_user')
        vals = dict(request.jsonrequest)
        products_return = []
        family_product = sorted(set(list(request.env['product.product'].with_user(cp_user).search([("categ_id.id", "!=", False)], order="categ_id").mapped("categ_id.name"))))
        for record in family_product:
            products_return.append({"categ_id" : record})
        return json.dumps(products_return)

    @http.route("/fcd_weight_scale_mrp/boxtypeget", type='json', auth='none')
    def fcd_weight_scale_mrp_getboxtype(self, **kwargs):
        cp_user = request.env.ref('fcd_weight_scale_mrp.res_user_fcd_checkpoint_user')
        vals = dict(request.jsonrequest)
        type_box_return = []
        product_ids = request.env['product.product'].with_user(cp_user).browse(int(vals['jsonSend']['product_id']))
        #type_box_ids = product_templ_id.secondary_uom_ids
        # type_box_ids = request.env['product.secondary.unit'].sudo().search([("product_tmpl_id", "=", product_templ_id)])
        for record in product_ids.secondary_uom_ids:
            if  record.factor != 0:
                type_box_return.append((record.id, record.name))
        return json.dumps(type_box_return)

    @http.route("/fcd_weight_scale_mrp/getWeight", type='json', auth='none')
    def fcd_weight_scale_mrp_getWeight(self):
        cp_user = request.env.ref('fcd_weight_scale_mrp.res_user_fcd_checkpoint_user')
        data = dict(request.jsonrequest)
        createdJson = {}
        LotEnv = request.env['fcd.checkpoint']
        try:
            weightGet = LotEnv.with_user(cp_user).get_weight(data)
            if 'error' in weightGet:
                createdJson['error'] = weightGet['error']
            else:
                createdJson = {
                    'weight_value': weightGet["weight_value"],
                }
        except Exception as e:
            createdJson = {}
            createdJson['error'] = "Scale not connected"
        return createdJson

    @http.route("/fcd_weight_scale_mrp/packaging", type='json', auth='none')
    def fcd_weight_scale_mrp_create_records(self):
        cp_user = request.env.ref('fcd_weight_scale_mrp.res_user_fcd_checkpoint_user')
        vals = dict(request.jsonrequest)
        try:
            #Create Log Modificar el vals dependiendo de si ya hay o no un movimiento del mismo producto
            log_id = request.env['fcd.weight.scale.log'].with_user(cp_user).create({
                'input_product_id': int(vals['input_product_id']),
                'output_product_id': int(vals['output_product_id']), #product.product en el portal
                'stock_move_id': int(vals['stock_move_id']),
                'checkpoint_id': int(vals['checkpoint_id']),
                'quantity': float(vals['quantity']),
                'weight_quantity': float(vals['weight_quantity']),
                'secondary_uom_id': int(vals['secondary_uom_id']),
                'date': fields.Datetime.now(),
                'packaging_date': fields.Datetime.now().strftime('%Y-%m-%d'),
            })
            log_return = []
            if not log_id:
                return {"error": "Weight log couldn't be recorded"}
            log_return.append({'log_id': log_id.id})
            return json.dumps(log_return)
        except Exception as e:
            _logger.warning(e)
            return {"error": "Unexpected error, please contact with administrator"}

    @http.route("/fcd_weight_scale_mrp/endLot", type='json', auth='none')
    def fcd_weight_scale_mrp_end_lot(self):
        cp_user = request.env.ref('fcd_weight_scale_mrp.res_user_fcd_checkpoint_user')
        vals = dict(request.jsonrequest)
        if vals['stock_move_id']:
            move_id = request.env['stock.move'].with_user(cp_user).browse(int(vals['stock_move_id']))
            move_id.purchase_line_id.write({
                "fcd_lot_finished": True
            })
            return move_id.purchase_line_id
        else:
            return {"error": "Stock move does not seems to exist, contact with Administrator"}

    # @http.route("/fcd_weight_scale_mrp/scaleEmulator", type='http', auth="user", website=False)
    # def scale_emulator(self):
    #     cp_user, user_id = self._get_cp_user_and_lang_context(request)
    #     weight_byte = ""
    #     port = 1001
    #     sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #     server_address = ('localhost', port)
    #     print('starting up on {} port {}'.format(*server_address))
    #     sock.bind(server_address)
    #     sock.listen(1)

    #     while True:
    #         weight = 0
    #         print('waiting for a connection')
    #         connection, client_address = sock.accept()
    #         try:
    #             print('connection from', client_address)
    #             while True:
    #                 data = connection.recv(16)
    #                 if b'$' in data:
    #                     weight = round(0.8*random.randint(1, 10), 3)
    #                     weight_format = str(weight)
    #                     weight_byte = weight_format.encode()
    #                     connection.sendall(weight_byte)
    #                     print(weight_format)
    #                     break
    #                 else:
    #                     print('no data from', client_address)
    #                     break
    #         finally:
    #             connection.close()
    #     return weight