# © 2026 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
{
    "name": "MRP Workorder Timeline",
    "summary": """
        Generates timeline view for work orders,
        showing the progress of each work order in a Gantt chart style.
        Based on web_timeline
    """,
    "author": "Solvos",
    "license": "AGPL-3",
    "version": "15.0.1.0.1",
    "category": "Manufacturing/Manufacturing",
    "website": "https://github.com/solvosci/slv-manufacture",
    "depends": ["mrp","web_timeline"],
    "data": [
        "views/mrp_workorder_views.xml",
    ],
    "uninstall_hook": "uninstall_hook",
}
