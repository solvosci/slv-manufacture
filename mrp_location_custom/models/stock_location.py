from odoo import fields, models


class StockLocation(models.Model):
    _inherit = 'stock.location'

    production_id = fields.Many2one(
        comodel_name='mrp.production',
        string='Manufacturing Order',
        copy=False,
        readonly=True,
        ondelete='set null',
        help='Manufacturing order this temporary location was created for.',
    )

    mrp_step = fields.Selection(
        selection=[
            ('pre_prod', 'Pre-Production'),
            ('in_process', 'In process'),
            ('post_prod', 'Post-Production'),
            ('pending_relocate', 'Pending relocation'),
        ],
        string='Manufacturing Step',
        copy=False,
    )

class StockLocationRoute(models.Model):
    _inherit = 'stock.location.route'

    production_id = fields.Many2one(
        comodel_name='mrp.production',
        string='Manufacturing Order',
        copy=False,
        readonly=True,
        ondelete='set null',
        help='Manufacturing order this temporary route was created for.',
    )