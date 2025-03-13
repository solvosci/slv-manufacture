# © 2025 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html

{
    "name": "MRP Production - Enable undo operation",
    "summary": """
        Enables undo a complete Production, updating stock inventory
    """,
    "author": "Solvos",
    "license": "LGPL-3",
    "version": "13.0.1.0.0",
    "category": "Manufacturing",
    "website": "https://github.com/solvosci/slv-manufacture",
    "depends": ["mrp"],
    "data": [
        "security/mrp_production_undo_security.xml",
        "views/mrp_production_views.xml",
    ],
}
