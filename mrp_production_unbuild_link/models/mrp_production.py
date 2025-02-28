# © 2025 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See https://www.gnu.org/licenses/lgpl-3.0.html

from odoo import fields, models


class ManufactureOrder(models.Model):
    _inherit = "mrp.production"

    finished_unbuild_id = fields.Many2one(
        comodel_name="mrp.unbuild",
        string="Unbuild",
        readonly=True,
        help="Finished unbuild for this production order.",
    )
