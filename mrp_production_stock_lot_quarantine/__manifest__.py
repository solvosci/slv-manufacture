# Copyright 2026 Solvos Consultoría Informática, S.L. (<https://www.solvos.es>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
{
    "name": "MRP Production Stock Lot Quarantine",
    "version": "19.0.1.0.0",
    "category": "Manufacturing/Manufacturing",
    "summary": "Propagates stock_lot_quarantine's purification state from "
                "consumed components to manufactured finished lots.",
    "author": "Solvos",
    "license": "LGPL-3",
    "depends": ["stock_lot_quarantine", "mrp"],
    "data": [
        "views/mrp_production_views.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
