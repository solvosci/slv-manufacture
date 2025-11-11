# © 2025 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See https://www.gnu.org/licenses/lgpl-3.0.html
{
    "name": "MRP Project WO Timesheet",
    "summary": """
        Add an extension between workorders to generate timesheets based on manufacturing productivity.
    """,
    "author": "Solvos",
    "license": "LGPL-3",
    "version": "15.0.1.0.0",
    "category": "Manufacturing",
    "website": "https://github.com/solvosci/slv-manufacture",
    "depends": [
        "hr_timesheet",
        "mrp_project",
    ],
    "data": [
        "views/mrp_production_views.xml",
    ],
}
