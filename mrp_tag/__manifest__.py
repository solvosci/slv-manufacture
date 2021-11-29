# © 2021 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html
{
    "name": "MRP Tags",
    "summary": """
        Adds tags to be used in MRP models
    """,
    "author": "Solvos",
    "license": "LGPL-3",
    "version": "13.0.1.1.0",
    "category": "Manufacturing",
    "website": "https://github.com/solvosci/slv-manufacture",
    "depends": ["mrp"],
    "data": [
        "security/ir.model.access.csv",
        "views/mrp_tag_views.xml",
    ],
    'installable': True,
}
