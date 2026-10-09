# Copyright 2026 Solvos Consultoría Informática
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import SUPERUSER_ID, api


def uninstall_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    wo_action = env.ref("mrp.mrp_workorder_todo", raise_if_not_found=False)
    if wo_action:
        wo_action.view_mode = "tree,kanban,form,calendar,pivot,graph,gantt"
