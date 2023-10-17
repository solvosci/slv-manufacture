# © 2023 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html
{
    "name": "MRP Production BOM Preview Report",
    "summary": """
    Set an Structure & Cost MRP report based on its consuptions
    """,
    "author": "Solvos",
    "license": "LGPL-3",
    "version": "14.0.1.0.1",
    'category': "Product",
    "website": "https://github.com/solvosci/slv-manufacture",
    "depends": [
        "mrp_account"
    ],
    "data": [
        "reports/mrp_production_report.xml",
        "reports/mrp_production_template.xml",
        "reports/mrp_report_bom_structure.xml",
        "views/assets.xml",
        "views/mrp_production_views.xml"
    ],
    'installable': True,
}
