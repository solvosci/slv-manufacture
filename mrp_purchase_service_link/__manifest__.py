# © 2023 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html
{
    "name": "MRP Purchase Service Link",
    "summary": """
        Adds link between the purchase order lines that are services with the manufacturing
    """,
    "author": "Solvos",
    "license": "LGPL-3",
    "version": "14.0.1.0.0",
    "category": "Inventory/Purchase",
    "website": "https://github.com/solvosci/slv-manufacture",
    "depends": ["purchase", "mrp"],
    "data": [
        "views/mrp_production_views.xml",
        "views/purchase_order_views.xml"
    ],
    'installable': True,
}
