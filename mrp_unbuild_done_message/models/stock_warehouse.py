# © 2024 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html

from odoo import models, fields

class StockWarehouse(models.Model):
    _inherit = 'stock.warehouse'

    unbuild_close_notify_users = fields.Many2many(
        comodel_name='res.users', 
        string="Users to notify for unbuilds closure", 
        help="Users to whom to send email for unbuilds closure associated with this warehouse", 
        domain=[('share', '=', False)]
    )
