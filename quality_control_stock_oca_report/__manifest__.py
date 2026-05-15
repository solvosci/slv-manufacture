# © 2026 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0.html
{
    "name": "Quality Control Stock OCA Report",
    "summary": """
        Enhancements to the quality control report for stock inspections,
        including improved layout and additional information.
    """,
    "author": "Solvos",
    "license": "AGPL-3",
    "version": "15.0.1.0.0",
    "category": "Inventory/Inventory",
    "website": "https://github.com/solvosci/slv-manufacture",
    "depends": ["quality_control_stock_oca", "quality_control_oca_report"],
    "data": [
        "report/qc_inspection_template.xml"
    ],
    'installable': True,
}
