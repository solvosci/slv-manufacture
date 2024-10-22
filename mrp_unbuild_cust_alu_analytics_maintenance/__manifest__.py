# © 2024 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
{
    "name": "Mrp Unbuild Cust Alu Analytics Maintenance",
    "summary": """
        Connect incidences with maintenance_equipment
    """,
    "version": "13.0.1.2.0",
    "category": "Manufacturing",
    "website": "https://github.com/solvosci/slv-manufacture",
    "author": "Solvos",
    "license": "AGPL-3",
    "depends": [
        "maintenance",
        "mrp_unbuild_cust_alu_analytics"
    ],
    "data": [
        "security/mrp_unbuild_cust_alu_analytics_maintenance_security.xml",
        "views/mrp_unbuild_views.xml",
        "views/maintenance_equipment_views.xml",
        "views/mrp_unbuild_incidence_views.xml",
    ],
}
