# © 2024 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):

    openupgrade.load_data(
        env.cr, "mrp_unbuild_done_message", "migrations/13.0.1.1.0/noupdate_changes.xml"
    )
