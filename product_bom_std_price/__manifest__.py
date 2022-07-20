# © 2022 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See https://www.gnu.org/licenses/lgpl-3.0.html
{
    "name": "Product BoM Standard Price",
    "summary": """
    For products based on standard price cost method, it will be calculated
    depending how is produced, based on BoM components and their costs
    """,
    "author": "Solvos",
    "license": "LGPL-3",
    "version": "11.0.1.0.0",
    "category": "Manufacturing",
    "website": "https://github.com/solvosci/slv-manufacture",
    "depends": ["mrp", "stock_account"],
    "installable": True,
    "post_init_hook": "post_init_hook",
}
