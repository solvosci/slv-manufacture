# © 2026 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See https://www.gnu.org/licenses/lgpl-3.0.html

from odoo import fields, models


class MrpBom(models.Model):
    _name = 'mrp.bom'
    # _inherit = ['mrp.bom', 'mail.thread', 'mail.activity.mixin']

    location_src_id = fields.Many2one(
        comodel_name='stock.location',
        string='Raw Materials Location',
        tracking=True,
        help='Default source location for the components of this Bill of '
             'Materials. Informative field, kept for reference (e.g. when '
             'the BoM was generated from a Manufacturing Order).',
    )
    location_dest_id = fields.Many2one(
        comodel_name='stock.location',
        string='Finished Products Location',
        tracking=True,
        help='Default destination location for the products manufactured '
             'with this Bill of Materials. Informative field, kept for '
             'reference (e.g. when the BoM was generated from a '
             'Manufacturing Order).',
    )
