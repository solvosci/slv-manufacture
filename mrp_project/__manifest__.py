# © 2022 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See https://www.gnu.org/licenses/lgpl-3.0.html
{
    "name": "Manufacture and Project bind",
    "summary": """
    For bind productions to projects through 2 fields, Many2one and One2many respectively. One project has many manufactures. 
    """,
    "author": "Solvos",
    "license": "LGPL-3",
    "version": "15.0.1.0.0",
    "category": "Manufacturing",
    "website": "https://github.com/solvosci/slv-manufacture",
    "depends": ["mrp", "project"],
    "data": [
        "views/project_project_views.xml",
        "views/mrp_production_views.xml",
    ],
    "installable": True,
}
