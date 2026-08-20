{
    "name": "MRP Production Stock Lot Quarantine Capture Zone",
    "version": "19.0.1.0.0",
    "category": "Manufacturing/Manufacturing",
    "description": "Propagates a manufactured lot's capture origins from "
                "its consumed components, so a later zone closure still "
                "blocks it.",
    "author": "Solvos",
    "license": "LGPL-3",
    "depends": [
        "stock_lot_quarantine_capture_zone",
        "mrp_production_stock_lot_quarantine",
    ],
    "data": [],
    "installable": True,
    "application": False,
    "auto_install": False,
}
