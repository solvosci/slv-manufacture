# Copyright 2026 Solvos Consultoría Informática, S.L. (<https://www.solvos.es>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
{
    "name": "MRP Production Stock Lot Quarantine Biological Zone",
    "version": "19.0.1.0.0",
    "category": "Manufacturing/Manufacturing",
    "description": "Propagates a manufactured lot's biological zone from "
                "its consumed components, alongside the capture zone "
                "origin, so its sanitary classification carries over too.",
    "author": "Solvos",
    "license": "LGPL-3",
    "depends": [
        "mrp_production_stock_lot_quarantine_capture_zone",
        "stock_lot_quarantine_biological_zone",
    ],
    "data": [],
    "installable": True,
    "application": False,
    "auto_install": False,
}
