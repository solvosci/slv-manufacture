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
    "version": "17.0.1.0.0",
    "category": "Manufacturing",
    "website": "https://github.com/solvosci/slv-manufacture",
    "depends": [
        "mrp_tag",
        "mrp_unbuild_bom_cust_qty",
        "stock_move_action_done_custdate"
    ],
    "data": [
        "security/mrp_unbuild_advanced_security.xml",
        "views/mrp_unbuild_views.xml",
        "views/mrp_unbuild_bom_total_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "mrp_unbuild_advanced/static/src/css/tablet_views.css",
        ],
    },
    'installable': True,
}
