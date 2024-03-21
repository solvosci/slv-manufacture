# © 2024 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3.0 (https://www.gnu.org/licenses/agpl-3.0.html)
{
    "name": "Mrp Unbuild Cust Alu Analytics",
    "summary": """
        Add incidences and process type to Unbuild, add custom report, add analytics to unbuilds
    """,
    "author": "Solvos",
    "license": "AGPL-3",
    "version": "13.0.1.0.0",
    "category": "Manufacturing",
    "website": "https://github.com/solvosci/slv-manufacture",
    "depends": ["mrp_unbuild_advanced", "mrp_unbuild_bom_cust_qty", "report_xlsx", "mrp_unbuild_qc"],
    "data": [
        "security/ir.model.access.csv",
        "data/ir_cron.xml",
        "data/qc_test.xml",
        "views/res_config_settings_view.xml",
        "views/mrp_unbuild_process_type_views.xml",
        "views/mrp_unbuild_views.xml",
        "views/mrp_unbuild_bom_total_views.xml",
        "views/mrp_bom_views.xml",
        "views/mrp_incidence_type_views.xml",
        "views/mrp_unbuild_incidence_views.xml",
        "views/mrp_unbuild_cust_alu_analytics_menus.xml",
        "reports/reports.xml",
    ],
    'installable': True,
}
