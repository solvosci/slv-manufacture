# Copyright 2026 Solvos Consultoría Informática, S.L. (<https://www.solvos.es>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "MRP Production Clasification",
    "summary": "Adds a Wizard to distribute quantities and lots for 'Classification' "
    "type manufacturing orders (bulk product -> N sizes/byproducts)",
    "author": "Solvos, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/manufacture",
    "category": "Manufacturing",
    "version": "19.0.1.0.0",
    "license": "AGPL-3",
    "depends": ["mrp", "stock"],
    "data": [
        "security/ir.model.access.csv",
        "wizard/mrp_classification_wizard_views.xml",
        "views/stock_picking_type_views.xml",
        "views/mrp_production_views.xml",
    ],
}
