# Copyright 2026 Solvos Consultoría Informática, S.L. (<https://www.solvos.es>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import models


class MrpClassificationWizard(models.TransientModel):
    _inherit = "mrp.classification.wizard"

    def _prepare_lines(self):
        super()._prepare_lines()
        tracked_lines = self.line_ids.filtered(lambda l: l.product_id.tracking != "none")
        if not tracked_lines:
            return
        products = [line.product_id for line in tracked_lines]
        names = self.env["stock.lot"]._suggest_names(products, self.production_id.company_id)
        for line, name in zip(tracked_lines, names):
            line.lot_name = name
