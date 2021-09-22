# © 2021 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (https://www.gnu.org/licenses/lgpl-3.0.html)

from odoo import fields, models


class QcInspection(models.Model):
    _inherit = "qc.inspection"

    unbuild_id = fields.Many2one(
        comodel_name="mrp.unbuild",
        readonly=True,
    )
