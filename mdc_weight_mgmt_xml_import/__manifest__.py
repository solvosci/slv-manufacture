# © 2025 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
{
    "name": "Weight Record Management XML Import",
    "summary": """
        Import XML files for weight records.
    """,
    "author": "Solvos",
    "license": "AGPL-3",
    "version": "17.0.1.3.0",
    "category": "Manufacture",
    "website": "https://github.com/solvosci/manufacture",
    "depends": [
        "mdc_weight_mgmt"],
    "data": [
        "security/ir.model.access.csv",
        "data/ir_cron_mdc_weight_import.xml",
        "data/mail_template_data.xml",
        "views/maintenance_equipment_views.xml",
        "views/mdc_weight_record_error_views.xml",
        "views/res_config_settings_views.xml",
    ],
}
