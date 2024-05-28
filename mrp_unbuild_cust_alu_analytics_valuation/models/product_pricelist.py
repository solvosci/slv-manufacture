# © 2024 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (https://www.gnu.org/licenses/lgpl-3.0.html)

from odoo import _, models, fields
from odoo.exceptions import ValidationError
from .mrp_unbuild_process_type import COST_UNIT_SELECTION_FIELDS

from datetime import timedelta


class ProductPricelist(models.Model):
    _inherit = "product.pricelist"
    _sql_constraints = [
        (
            "unbuild_process_type_unique",
            "unique(unbuild_process_type_id, unbuild_process_type_cost, company_id)",
            "Process type and cost type must unique by company!",
        )
    ]

    unbuild_process_type_id = fields.Many2one(
        comodel_name="mrp.unbuild.process.type",
        readonly=True,
        copy=False,
        ondelete="restrict",
    )
    unbuild_process_type_cost = fields.Selection(
        selection=COST_UNIT_SELECTION_FIELDS,
        default=False,
        readonly=True,
        copy=False,
    )

    def write(self, values):
        if (
            "active" in values
            and values.get("active", False)
            and self.unbuild_process_type_id
        ):
            raise ValidationError(_(
                "Cannot activate a pricelist with a linked unbuild process type!"
            ))
        return super().write(values)
    
    def unlink(self):
        if self.unbuild_process_type_id:
            raise ValidationError(_(
                "Cannot delete a pricelist with a linked unbuild process type!"
            ))
        return super().unlink()
    
    def _update_cost_value(self, cost_value):
        self.ensure_one()
        if not self.unbuild_process_type_id:
            return
        today = fields.Date.today()
        yesterday = today - timedelta(days=1)
        # There are the following cases:
        # 1. Change today's cost. => an item starting from today is found
        # 2. Close a past cost => an item starting from before today (and not closed) is found => close with yesterday
        item_ids = self.with_context(active_test=False).item_ids
        # If should be only one
        item_1 = item_ids.filtered(
            lambda x: x.date_start and x.date_start <= today and not x.date_end
        )
        if item_1 and item_1.date_start == today:
            item_1.write({"fixed_price": cost_value})
        else:
            item_1.write({"date_end": yesterday})
            self.item_ids.create({
                "pricelist_id": self.id,
                "applied_on": "3_global",
                "compute_price": "fixed",
                "fixed_price": cost_value,
                "date_start": today,
                "date_end": False,
            })

    def action_view_costs_pricelist_items(self):
        self.ensure_one()
        action = {
            "type": "ir.actions.act_window",
            "name": _("Unit Costs History"),
            "res_model": "product.pricelist.item",
            "view_mode": "tree",
            "domain": [
                ("pricelist_id", "=", self.id),
            ],
            "context": {"search_default_inactive": True},
        }
        return action
