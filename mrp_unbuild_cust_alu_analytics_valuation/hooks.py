# © 2024 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

import logging
from odoo import SUPERUSER_ID, api


def post_init_hook(cr, registry):
    logger = logging.getLogger("odoo.addons.mrp_unbuild_cust_alu_analytics_valuation")
    logger.info(
        "Creating cost history pricelists for existing unbuild process types..."
    )
    env = api.Environment(cr, SUPERUSER_ID, {})
    upt_ids = env["mrp.unbuild.process.type"].search([])
    upt_ids._create_costs_pricelists()
    logger.info(
        "Created cost history pricelists for %d unbuild process type(s)" % len(upt_ids)
    )
