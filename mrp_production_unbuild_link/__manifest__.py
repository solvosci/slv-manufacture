# © 2025 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See https://www.gnu.org/licenses/lgpl-3.0.html
{
    "name": "MRP Production - Link to Unbuild",
    "summary": """
        For a MRP Production provides a link to linked Unbuild
    """,
    "author": "Solvos",
    "license": "LGPL-3",
    "version": "15.0.1.0.0",
    "category": "Manufacturing",
    "website": "https://github.com/solvosci/slv-manufacture",
    "depends": ["mrp"],
    "data": ["views/mrp_production_views.xml"],
    "post_init_hook": "post_init_hook",
}
