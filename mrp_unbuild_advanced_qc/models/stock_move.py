# © 2021 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (https://www.gnu.org/licenses/lgpl-3.0.html)

from odoo import _, models
from odoo.exceptions import ValidationError


class StockMove(models.Model):
    _inherit = "stock.move"

    def _check_safe_removal(self):
        super()._check_safe_removal()
        inspections = self.env["qc.inspection"].search([
            ("unbuild_id", "=", self.unbuild_id.id),
            ("object_id", "!=", False),
        ])
        if inspections:
            raise ValidationError(_(
                "There are %d inspections(s) linked to the current generated"
                " moves. Please remove them before backing unbuild to draft")
                % len(inspections)
            )
