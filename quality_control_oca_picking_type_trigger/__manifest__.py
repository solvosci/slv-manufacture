# © 2026 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
{
    "name": "Quality Control OCA Picking Type Trigger",
    "summary": """
        Add a trigger to create quality control points to picking types.
    """,
    "author": "Solvos",
    "license": "AGPL-3",
    "version": "15.0.1.0.0",
    "category": "Manufacturing/Manufacturing",
    "website": "https://github.com/solvosci/slv-manufacture",
    "depends": ["quality_control_stock_oca"],
    "data": [
        "security/ir.model.access.csv",
        "views/stock_picking_type_views.xml",
    ],
}
