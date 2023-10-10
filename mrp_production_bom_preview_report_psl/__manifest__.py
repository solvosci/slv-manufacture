# © 2023 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html
{
    "name": "MRP Production BOM Preview Report PSL",
    "summary": """
    Link between mrp_production_bom_preview_report and mrp_purchase_service_link
    """,
    "author": "Solvos",
    "license": "LGPL-3",
    "version": "14.0.1.0.0",
    "category": "Inventory/Purchase",
    "website": "https://github.com/solvosci/slv-manufacture",
    "depends": [
        "mrp_production_bom_preview_report",
        "mrp_purchase_service_link"
    ],
    "data": [
        "reports/mrp_production_template.xml",
        "reports/mrp_report_bom_structure.xml"
    ],
    'installable': True,
}
