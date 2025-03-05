# © 2025 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
{
    "name": "Weight Record XLSX Report",
    "summary": """
        Implements a XLSX report option on the wizard assistant.
    """,
    "author": "Solvos",
    "license": "AGPL-3",
    "version": "17.0.1.0.0",
    "category": "Manufacture",
    "website": "https://github.com/solvosci/manufacture",
    "depends": [
        "mdc_weight_mgmt",
        "report_xlsx"
    ],
    "data": [
        "reports/report_view.xml",
        "wizard/mdc_weight_record_report_wizard_view.xml",
    ],
}
