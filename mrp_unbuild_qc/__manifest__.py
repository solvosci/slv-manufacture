# © 2021 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html
{
    "name": "MRP Unbuild Quality Control",
    "summary": """
        Enable inspection of product movements from unbuild order
    """,
    "author": "Solvos",
    "license": "LGPL-3",
    "version": "13.0.1.1.0",
    "category": "Manufacturing",
    "website": "https://github.com/solvosci/slv-manufacture",
    "depends": ["quality_control_mrp_oca"],
    "data": [
        "views/qc_inspection_views.xml",
        "views/mrp_unbuild_views.xml",
        "views/stock_move_line_views.xml"
    ],
    'installable': True,
}
