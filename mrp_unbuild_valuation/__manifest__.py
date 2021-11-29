# © 2021 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html
{
    "name": "MRP Unbuild Valuation",
    "summary": """
        Adds valuation view for done unbuilds and new valuation methods
    """,
    "author": "Solvos",
    "license": "LGPL-3",
    "version": "13.0.2.0.0",
    "category": "Manufacturing",
    "website": "https://github.com/solvosci/slv-manufacture",
    "depends": ["mrp", "stock_account"],
    "data": [
        "views/mrp_unbuild_views.xml",
    ],
    'installable': True,
}
