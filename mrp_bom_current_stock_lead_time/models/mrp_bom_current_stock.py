# © 2026 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3.0 - See (https://www.gnu.org/licenses/agpl-3.0).

from collections import defaultdict
from odoo import api, fields, models


class BomRouteCurrentStock(models.TransientModel):
    _inherit = "mrp.bom.current.stock"

    total_lead_time_days = fields.Float(
        string="Total Lead Time (days)",
        compute="_compute_total_lead_time_days",
        help="Manufacturing lead time of the product plus, for each BoM level, "
        "the slowest component that is not covered by stock.",
    )

    def do_explode(self):
        self.ensure_one()
        self.line_ids.unlink()
        return super().do_explode()

    @api.depends(
        "product_id.produce_delay",
        "line_ids.bom_level",
        "line_ids.needs_supply",
        "line_ids.lead_time_days",
    )
    def _compute_total_lead_time_days(self):
        for wizard in self:
            wizard.total_lead_time_days = wizard._get_root_lead_time() + sum(
                wizard._get_slowest_lead_time_by_level().values()
            )

    def _get_root_lead_time(self):
        self.ensure_one()
        return self.product_id.produce_delay

    def _get_slowest_lead_time_by_level(self):
        """Return {bom_level: slowest lead time among its components}.

        Components are created depth first, so the descendants of a component
        are the following lines with a higher level. Those below a component
        covered by stock are not needed and are skipped.
        """
        self.ensure_one()
        slowest = defaultdict(float)
        covered_level = None
        for line in self.line_ids.sorted("id"):
            if covered_level is not None and line.bom_level > covered_level:
                continue
            covered_level = None if line.needs_supply else line.bom_level
            slowest[line.bom_level] = max(slowest[line.bom_level], line.lead_time_days)
        return slowest
