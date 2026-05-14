# © 2026 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0.html
{
    "name": "Quality Control OCA Report",
    "summary": """
        Add report for quality control OCA
    """,
    "author": "Solvos",
    "license": "AGPL-3",
    "version": "15.0.1.0.0",
    "category": "Inventory/Inventory",
    "website": "https://github.com/solvosci/slv-manufacture",
    "depends": ["quality_control_oca"],
    "data": [
        "security/ir.model.access.csv",
        "wizard/qc_inspection_report_wizard_view.xml",
        "views/qc_inspection_views.xml",
        "report/qc_inspection_report.xml",
        "report/qc_inspection_template.xml"
    ],
    'installable': True,
}
