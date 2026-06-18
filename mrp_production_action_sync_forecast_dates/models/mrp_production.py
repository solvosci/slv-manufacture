# © 2026 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See https://www.gnu.org/licenses/lgpl-3.0.html

from odoo import _, models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    def action_sync_forecast_dates(self):
        selected_mos = self.filtered(
            lambda p: p.state in ["draft", "confirmed"] and not p.is_planned
        )
        if not selected_mos:
            return {}, self.browse()
        all_needed_products = selected_mos.move_raw_ids.product_id
        precursor_mos = self.env["mrp.production"].search([
            ("product_id", "in", all_needed_products.ids),
            ("state", "in", ["draft", "confirmed"]),
            ("is_planned", "=", False),
        ])
        all_mos = selected_mos | precursor_mos
        processed = self.env["mrp.production"]
        track_changes = {}

        def process_mo_by_product(mo):
            nonlocal processed
            if mo in processed:
                return
            my_components = mo.move_raw_ids.product_id
            supplier_mos = all_mos.filtered(
                lambda p: p.product_id in my_components and p != mo
            )
            for supplier_mo in supplier_mos:
                process_mo_by_product(supplier_mo)
            dates = []
            for move in mo.move_raw_ids:
                component_suppliers = all_mos.filtered(
                    lambda p: p.product_id == move.product_id
                )
                if component_suppliers:
                    dates.extend(
                        component_suppliers.mapped("date_planned_finished")
                    )
                elif move.forecast_expected_date:
                    dates.append(move.forecast_expected_date)
            if dates:
                max_forecast = max(dates)
                if (
                    not mo.date_planned_start
                    or max_forecast > mo.date_planned_start
                ):
                    mo.write({"date_planned_start": max_forecast})
                    mo._onchange_date_planned_start()
                    track_changes[mo.id] = {
                        "name": mo.name,
                        "new_date": mo.date_planned_start.strftime(
                            "%Y-%m-%d %H:%M:%S"
                        ),
                    }
            processed |= mo

        for mo in selected_mos:
            process_mo_by_product(mo)
        return track_changes, selected_mos

    def action_sync_forecast_dates_notify(self):
        track_changes, selected_mos = self.action_sync_forecast_dates()
        message_lines = []
        if track_changes:
            message_lines.append(_("Updated Manufacturing Orders:"))
            for mo_info in track_changes.values():
                message_lines.append(
                    _("• %(mo_name)s ➔ New Date: %(mo_new_date)s", mo_name=mo_info['name'], mo_new_date=mo_info['new_date']) 
                )
        unchanged_selected = selected_mos.filtered(
            lambda m: m.id not in track_changes
        )
        if unchanged_selected:
            if message_lines:
                message_lines.append("")
            message_lines.append(_(
                "The following orders could not be updated"
                " (please check each one):"
            ))
            for mo in unchanged_selected:
                message_lines.append(f"• {mo.name}")
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Forecast Sync Report"),
                "message": "\n".join(message_lines),
                "sticky": True,
                "type": "warning" if unchanged_selected else "success",
                "next": {"type": "ir.actions.act_window_close"},
            },
        }
