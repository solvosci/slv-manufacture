# © 2022 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html

from odoo import models
from odoo.http import request


class IrHttp(models.AbstractModel):
    _inherit = 'ir.http'

    @classmethod
    def _get_translation_frontend_modules_name(cls):
        modules = super(IrHttp, cls)._get_translation_frontend_modules_name()
        return modules + ['fcd_weight_scale_mrp']

    @classmethod
    def _get_frontend_langs(cls):
        if request and request.is_frontend:
            return [request.env.context['lang']]
        return super(IrHttp, cls)._get_frontend_langs()
