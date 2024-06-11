# © 2022 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See https://www.gnu.org/licenses/lgpl-3.0.html
{
    "name": "Propagates project analytic account to MRP account moves",
    "summary": """
        For those MRPs linked to projects, when account moves are generated,
        project analytic account is automatically set
    """,
    "author": "Solvos",
    "license": "LGPL-3",
    "version": "15.0.1.2.0",
    "category": "Manufacturing",
    "website": "https://github.com/solvosci/slv-manufacture",
    "depends": ["mrp_project", "mrp_account"],
    "data": [
        "views/account_move_line_view.xml",
    ],
    "installable": True,
    "post_init_hook": "post_init_hook",
}
