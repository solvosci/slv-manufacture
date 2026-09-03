# Copyright 2026 Solvos Consultoría Informática, S.L. (<https://www.solvos.es>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

import re

from odoo import api, fields, models


class StockLot(models.Model):
    _inherit = "stock.lot"

    @api.onchange("product_id")
    def _onchange_product_id_suggest_name(self):
        for lot in self.filtered(lambda x: x.product_id):
            lot.name = lot._suggest_name(lot.product_id, lot.company_id)

    def action_suggest_name(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "res_model": "stock.lot.suggest.name.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {"default_lot_id": self.id},
        }

    def _suggest_name(self, product, company=None):
        return self._suggest_names([product], company)[0]

    def _suggest_names(self, products, company=None):
        """Suggest a name for each product in `products` (repeats allowed,
        one name returned per entry, same order) using the
        CCCC_YYYYMMDD_NN pattern:
        - CCCC: the product's short code.
        - YYYYMMDD: today's date.
        - NN: a daily counter per product, computed from existing
        lots with that prefix.
        """
        today = fields.Date.context_today(self)
        date_str = today.strftime("%Y%m%d")

        prefixes = {
            product.id: f"{self._suggest_name_prefix_code(product)}_{date_str}_"
            for product in set(products)
        }

        domain = [("product_id", "in", list(prefixes.keys()))]
        company_id = company.id if company else False
        if company_id:
            domain += ["|", ("company_id", "=", company_id), ("company_id", "=", False)]
        existing_lots = self.env["stock.lot"].sudo().search(domain)

        next_seq = {}
        for product_id, prefix in prefixes.items():
            max_seq = 0
            for lot in existing_lots:
                if lot.product_id.id != product_id or not lot.name.startswith(prefix):
                    continue
                suffix = lot.name[len(prefix):]
                if suffix.isdigit():
                    max_seq = max(max_seq, int(suffix))
            next_seq[product_id] = max_seq + 1

        names = []
        for product in products:
            prefix = prefixes[product.id]
            seq = next_seq[product.id]
            names.append(f"{prefix}{seq:02d}")
            next_seq[product.id] = seq + 1
        return names

    def _suggest_name_prefix_code(self, product):
        if product.default_code:
            return product.default_code
        attr_values = product.product_template_attribute_value_ids.mapped("name")
        if attr_values:
            code = re.sub(r"[\s/]+", "-", "-".join(attr_values)).strip("-")
            if code:
                return code
        return "SC"
