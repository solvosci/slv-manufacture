# Copyright 2026 Solvos Consultoría Informática, S.L. (<https://www.solvos.es>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
{
    "name": "Stock Lot Name Sequence",
    "version": "19.0.1.0.0",
    "category": "Inventory",
    "website": "https://github.com/solvosci/slv-manufacture",
    "summary": "Suggests lot/serial names using a CCCC_YYYYMMDD_NN pattern "
                "(product code, date, daily sequence)",
    "author": "Solvos",
    "license": "LGPL-3",
    "depends": ["stock"],
    "data": [
        "security/ir.model.access.csv",
        "views/stock_lot_views.xml",
        "wizard/stock_lot_suggest_name_wizard_views.xml",
    ],
    "installable": True,
    "application": False,
}
