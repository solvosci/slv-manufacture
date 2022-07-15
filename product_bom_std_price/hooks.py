# © 2022 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See https://www.gnu.org/licenses/lgpl-3.0.html

from odoo import api, SUPERUSER_ID


def post_init_hook(cr, registry, vals=None):
    env = api.Environment(cr, SUPERUSER_ID, {})
    products = env["product.product"].search([]).filtered(
        lambda x: x.cost_method == "standard"
    )
    boms = products.sudo().mapped("component_bom_ids")
    if boms:
        boms.update_product_standard_price()
