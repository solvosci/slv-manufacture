# -*- coding: utf-8 -*-

import logging
import datetime
from odoo import models, fields, _

class Lot(models.Model):
    """
    Main data for Lot (Scale Orders Lots)
    """
    _name = 'weight.scale.lot'
    _description = 'Lot'

    # _sql_constraints = [('lot_name_unique', 'UNIQUE(name)', _('The selected lot name already exists')),]

    def _default_date(self):
        #return fields.Datetime.from_string(fields.Datetime.now())
        return fields.Datetime.now()
    def _default_uom(self):
        return self.env.ref('product.product_uom_kgm')

    name = fields.Char(
        'MO',
        required=True)
    product_id = fields.Many2one(
        'product.product',
        string='Product (Standard)',
        required=True)
    weight =fields.Float(
        'Weight',
        required=True)
    finished = fields.Boolean(
        'Lot finished',
        default=False)