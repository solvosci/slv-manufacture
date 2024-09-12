# © 2023 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See https://www.gnu.org/licenses/lgpl-3.0.html
{
    "name": "Manufacture Workcenter Dashboard",
    "summary": """
        Enables workcenter dashboard, disabled by default in Odoo
    """,
    "author": "Solvos",
    "license": "LGPL-3",
    "version": "15.0.1.0.0",
    "category": "Manufacturing",
    "website": "https://github.com/solvosci/slv-manufacture",
    "depends": ["mrp"],
    "data": ["views/mrp_workcenter_views.xml"],
    "installable": True,
}
