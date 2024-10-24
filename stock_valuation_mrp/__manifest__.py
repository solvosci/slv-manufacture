# © 2022 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html
{
    "name": "Stock Valuation MRP",
    "summary": """
        Link between Stock Valuation and MRP modules
    """,
    "author": "Solvos",
    "license": "LGPL-3",
    "version": "13.0.2.3.0",
    "category": "stock",
    "website": "https://github.com/solvosci/slv-stock",
    "depends": ["stock_valuation", "mrp_unbuild_advanced"],
    "data": ["views/mrp_unbuild_views.xml"],
    'installable': True,
}
