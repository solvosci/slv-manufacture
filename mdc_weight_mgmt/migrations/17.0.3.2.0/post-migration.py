# # © 2026 Solvos Consultoría Informática (<http://www.solvos.es>)
# # License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html
from odoo import fields, api, SUPERUSER_ID
from datetime import timedelta


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    today = fields.Date.today()
    weight = env['mdc.weight.declared.weight']
    products = env['product.product'].search([])

    for product in products:
        declared_weight = product.mdc_weight_dec_qty
        if not declared_weight:
            continue
        weight.create({
            'product_id': product.id,
            'date_from': False,
            'date_to': today - timedelta(days=1),
            'declared_weight': declared_weight
        })
        weight.create({
            'product_id': product.id,
            'date_from': today,
            'date_to': False,
            'declared_weight': declared_weight
        })
