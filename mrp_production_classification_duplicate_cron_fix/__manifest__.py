# Copyright 2026 Solvos Consultoría Informática, S.L. (<https://www.solvos.es>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
{
    "name": "MRP Production Classification - Fix Duplicate Lot Lines",
    "summary": "Cron that merges the leftover placeholder move line "
    "(quantity 1) Odoo's own done-validation leaves next to the real one on "
    "a classification order's main product.",
    "author": "Solvos",
    "website": "https://github.com/solvosci/slv-manufacture",
    "category": "Manufacturing",
    "version": "19.0.1.0.0",
    "license": "LGPL-3",
    "depends": ["mrp_production_classification"],
    "data": [
        "data/ir_cron_data.xml",
    ],
}
