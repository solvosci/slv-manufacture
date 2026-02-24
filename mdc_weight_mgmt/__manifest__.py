# © 2025 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html
{
    "name": "Weight Record Management",
    "summary": """
        Implements record weight data and generates a
        PDF or HTML report for displaying the collected information.
    """,
    "author": "Solvos",
    "license": "LGPL-3",
    "version": "17.0.3.0.1",
    "category": "Manufacture",
    "website": "https://github.com/solvosci/manufacture",
    "depends": ["product","maintenance"],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "wizard/mdc_weight_record_report_wizard_view.xml",
        "views/mdc_weight_record_views.xml",
        "views/mdc_weight_shift_views.xml",
        "views/product_views.xml",
        "views/res_config_settings_views.xml",
        "reports/mdc_weight_report.xml",
        "reports/mdc_weight_template.xml",
        "views/mdc_weight_mgmt_menu.xml",
    ],
}
