# -*- coding: utf-8 -*-
import json
import logging
import pdb
from odoo.http import request
from odoo import http, fields, _
from datetime import date

_logger = logging.getLogger(__name__)

class WeightScaleCheckPoint(http.Controller):
    # Common Functions
    def _get_client_ip(self):
        remote_ip = request.httprequest.environ.get('HTTP_X_REAL_IP')
        if not remote_ip:
            remote_ip = request.httprequest.environ.get('REMOTE_ADDR')
        return remote_ip

    def _get_cp_user_and_lang_context(self, request):
        cp_user = request.env.ref('weight_scale.weight_packaging_user_cp')
        context = request.env.context.copy()
        context.update({'lang': cp_user.sudo().lang})
        request.env.context = context
        return cp_user
    
    @http.route('/weight_scale/list/', auth='public')
    def index(self, **kw):
        return "Hello, world"

    @http.route("/weight_scale/basculaTry", type='http', auth='none')
    def cp_weight(self, **kwargs):
        cp_user = self._get_cp_user_and_lang_context(request)
        chkpoints = request.env['weight.scale.chkpoint'].with_user(cp_user).search([])
        
        return request.render('weight_scale.chkpoint_weight',
                {'chkpoints': chkpoints})

    @http.route("/weight_scale/cp/lotactive", type='json', auth='none')
    def cp_weight_lotactive(self, **kwargs):
        cp_user = self._get_cp_user_and_lang_context(request)
        lots = request.env['weight.scale.lot'].with_user(cp_user).search(
        [('finished', '=', False)], order='name')
        lots_return = {}
        for lot in lots:
            lots_return.update({lot.id: lot.name, str(lot.id) + "code": lot.product_id.id})
        return json.dumps(lots_return)
        

        


# class WeightScale(http.Controller):
#     @http.route('/weight_scale/weight_scale/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/weight_scale/weight_scale/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('weight_scale.listing', {
#             'root': '/weight_scale/weight_scale',
#             'objects': http.request.env['weight_scale.weight_scale'].search([]),
#         })

#     @http.route('/weight_scale/weight_scale/objects/<model("weight_scale.weight_scale"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('weight_scale.object', {
#             'object': obj
#         })
