# © 2021 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html
{
    "name": "MRP Unbuild Advanced additions",
    "summary": """
        Adds some improvements for Unbuilds: move back to draft,
        custom date, shift data, tags, etc
    """,
    "author": "Solvos",
    "license": "LGPL-3",
    "version": "13.0.2.11.0",
    "category": "Manufacturing",
    "website": "https://github.com/solvosci/slv-manufacture",
    "depends": ["mrp_tag", "stock_move_action_done_custdate"],
    "data": [
        "views/assets.xml",
        "security/mrp_unbuild_advanced_security.xml",
        "views/mrp_unbuild_views.xml",
        "views/mrp_unbuild_bom_total_views.xml",
    ],
    'installable': True,
}
