from datetime import timedelta

from odoo import Command, fields
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    priceslist_vals_list = []
    cost_field = "cost_unit_indirect"
    cost_label = "Indirect unit cost"
    now = fields.Datetime.now()
    prev_now = now - timedelta(seconds=1)

    process_types = env["mrp.unbuild.process.type"].with_context(active_test=False).search([
        ("cost_pricelist_ids", "not any", [
            ("unbuild_process_type_cost", "=", cost_field)
        ]),
    ])

    for type in process_types:
        item_list = [Command.create({
            "applied_on": "3_global",
            "date_end": prev_now,
            "compute_price": "fixed",
            "fixed_price": type[cost_field],
        })]
        item_list.append(Command.create({
            "applied_on": "3_global",
            "date_start": now,
            "date_end": False,
            "compute_price": "fixed",
            "fixed_price": type[cost_field],
        }))
        priceslist_vals_list.append({
            "unbuild_process_type_id": type.id,
            "unbuild_process_type_cost": cost_field,
            "company_id": type.company_id.id,
            "name": f"{type.name} - {cost_label}",
            "active": False,
            "item_ids": item_list,
        })
    if priceslist_vals_list:
        env["product.pricelist"].sudo().create(priceslist_vals_list)