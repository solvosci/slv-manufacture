# © 2022 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See https://www.gnu.org/licenses/lgpl-3.0.html

from odoo import api, SUPERUSER_ID
import logging

_logger = logging.getLogger(__name__)


def post_init_hook(cr, registry, vals=None):
    env = api.Environment(cr, SUPERUSER_ID, {})
    mrps = env["mrp.production"].search([
        ("project_id", "!=", False),
        ("state", "=", "done"),
    ])
    _logger.info(
        "Updating analytic account in account move lines for %d MOs..."
        % len(mrps)
    )
    for mrp in mrps:
        mrp._update_account_analytic()
