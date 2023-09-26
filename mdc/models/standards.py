# -*- coding: utf-8 -*-

import datetime
from odoo import api, models, fields, _
from odoo.exceptions import UserError


class Std(models.Model):
    """
    Main data for Lot (Manufacturing Orders Lots)
    """
    _name = 'mdc.std'
    _inherits = {'product.product': 'product_id'}
    _description = 'Standards'

    _sql_constraints = [
        ('product_id_unique', 'UNIQUE(product_id)',
         _("There's another standard with the same product")),
    ]

    product_id = fields.Many2one(
        'product.product',
        string='Product',
        required=True,
        copy=False,
        ondelete='restrict')
    std_loss = fields.Float(
        'Std Loss')
    std_yield_product = fields.Float(
        'Std Yield Product',
        digits=(10,3))
    std_speed = fields.Float(
        'Std Speed',
        digits=(10,3))
    std_yield_sp1 = fields.Float(
        'Std Yield Subproduct 1',
        digits=(10,3))
    std_yield_sp2 = fields.Float(
        'Std Yield Subproduct 2',
        digits=(10,3))
    std_yield_sp3 = fields.Float(
        'Std Yield Subproduct 3',
        digits=(10,3))
    active = fields.Boolean(
        'Active',
        default=True)

    @api.multi
    def copy(self):
        # we don´t want to duplicate because this action create a new product with out control
        raise UserError(_('It not possible to duplicate the record, please create a new one'))
