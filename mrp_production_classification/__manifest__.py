# Copyright 2026 Solvos Consultoría Informática, S.L. (<https://www.solvos.es>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
{
    "name": "MRP Production Clasification",
    "summary": "Adds a Wizard to distribute quantities and lots for 'Classification' "
    "type manufacturing orders (bulk product -> N sizes/byproducts)",
    "author": "Solvos",
    "website": "https://github.com/solvosci/slv-manufacture",
    "category": "Manufacturing",
    "version": "19.0.1.0.0",
    "license": "LGPL-3",
    "depends": ["mrp"],
    "data": [
        "security/ir.model.access.csv",
        "wizard/mrp_classification_wizard_views.xml",
        "views/stock_picking_type_views.xml",
        "views/mrp_production_views.xml",
    ],
}
