# Copyright 2026 Solvos Consultoría Informática, S.L. (<https://www.solvos.es>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    def _prepare_finished_lot_capture_origin_vals(self, finished_lot, origin):
        vals = super()._prepare_finished_lot_capture_origin_vals(finished_lot, origin)
        vals["sanitary_guide_id"] = origin.sanitary_guide_id.id
        return vals
