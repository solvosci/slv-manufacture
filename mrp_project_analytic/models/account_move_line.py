# © 2024 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See https://www.gnu.org/licenses/lgpl-3.0.html

from odoo import models, fields


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    analytic_mrp_from_child = fields.Boolean(readonly=True)
