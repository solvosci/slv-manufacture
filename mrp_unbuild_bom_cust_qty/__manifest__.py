# © 2021 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html
{
    "name": "MRP Unbuild Custom Quantities",
    "summary": """
        Enables addding custom quantities for an unbuild that comes from a BoM.
    """,
    "author": "Solvos",
    "license": "LGPL-3",
    "version": "17.0.1.0.1",
    "category": "Manufacturing",
    "website": "https://github.com/solvosci/slv-manufacture",
    "depends": ["mrp"],
    "excludes": ["mrp_unbuild_tracked_raw_material"],
    "data": [
        "security/mrp_unbuild_bom_cust_qty_security.xml",
        "security/ir.model.access.csv",
        "views/mrp_unbuild_views.xml",
        "views/mrp_unbuild_bom_quants.xml",
        "views/mrp_unbuild_bom_total.xml",
        "views/res_config_settings_views.xml",
    ],
    'assets': {
        'web.assets_backend': [
            'mrp_unbuild_bom_cust_qty/static/src/**/*',
        ],
    },
    'installable': True,
}
