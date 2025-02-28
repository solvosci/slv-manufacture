# © 2025 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See https://www.gnu.org/licenses/lgpl-3.0.html

from odoo import api, SUPERUSER_ID
import logging

_logger = logging.getLogger(__name__)


def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    unbuild_ids = env["mrp.unbuild"].search([
        ("mo_id", "!=", False),
        ("state", "=", "done"),
    ])
    _logger.info(
        "Linking %d finished Unbuilds to their related MOs..."
        % len(unbuild_ids)
    )
    unbuild_ids._update_mrp_from_unbuild()
