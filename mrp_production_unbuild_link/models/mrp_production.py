# © 2025 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See https://www.gnu.org/licenses/lgpl-3.0.html

from odoo import fields, models


class ManufactureOrder(models.Model):
    _inherit = "mrp.production"

    finished_unbuild_ids = fields.One2many(
        comodel_name="mrp.unbuild",
        inverse_name="mo_id",
        domain=[("state", "=", "done")],
        string="Unbuild",
        help="Finished unbuilds for this production order.",
    )
