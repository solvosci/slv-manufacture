# © 2023 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html
{
    "name": "MRP Timesheet Link",
    "summary": """
        Adds link between timesheet and production orders
    """,
    "author": "Solvos",
    "license": "LGPL-3",
    "version": "14.0.1.0.1",
    "category": "Inventory/Purchase",
    "website": "https://github.com/solvosci/slv-manufacture",
    "depends": ["hr_timesheet", "mrp"],
    "data": [
        "views/mrp_production_views.xml",
        "views/project_task_views.xml"
    ],
    'installable': True,
}
