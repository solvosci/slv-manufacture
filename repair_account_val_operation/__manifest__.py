# © 2026 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See https://www.gnu.org/licenses/lgpl-3.0.html
{
    "name": "Repair Account Valuation Operation",
    "summary": """
        Extends functionality of stock_account_val_operation to include valuation operations for reparations processes.
    """,
    "author": "Solvos",
    "license": "LGPL-3",
    "version": "15.0.1.0.0",
    "category": "Inventory/Inventory",
    "website": "https://github.com/solvosci/slv-manufacture",
    "depends": [
        "stock_account_val_operation",
        "repair"
    ],
    "data": [],
    'installable': True,
    "pre_init_hook": "pre_init_hook",
}
