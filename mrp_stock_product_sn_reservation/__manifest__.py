# © 2025 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html
{
    "name": "MRP Productions - Advanced S/N reservation",
    "summary": """
        Enables s/n secure reservation in production consume moves,
        preventing undesired situations when a s/n is manually assigned
    """,
    "author": "Solvos",
    "license": "LGPL-3",
    "version": "15.0.1.0.1",
    "category": "Manufacturing/Manufacturing",
    "website": "https://github.com/solvosci/slv-manufacture",
    "depends": ["mrp", "stock_product_sn_reservation"],
    "data": [
        "security/mrp_stock_product_sn_reservation.xml",
        "views/mrp_production_views.xml",
    ],
}
