# © 2021 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html
{
    "name": "Unbuild Maintenance",
    "summary": """
        Bind unbuilds with maintenances
    """,
    "version": "13.0.1.0.0",
    "category": "Manufacturing",
    "website": "https://github.com/solvosci/slv-manufacture",
    "author": "Solvos",
    "license": "LGPL-3",
    "depends": [
        "maintenance",
        "mrp_unbuild_cust_alu_analytics"
    ],
    "data": [
        "views/maintenance_equipment_views.xml",
        "views/mrp_unbuild_views.xml",
    ],
}
