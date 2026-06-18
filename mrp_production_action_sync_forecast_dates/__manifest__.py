# © 2026 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See https://www.gnu.org/licenses/lgpl-3.0.html
{
    "name": "MRP Production Sync Forecast Dates",
    "summary": """
        Creates a server action to sync the forecast dates
        of the last expected component with the planned start date of the production order.
    """,
    "author": "Solvos",
    "license": "LGPL-3",
    "version": "15.0.1.0.0",
    "category": "Manufacturing",
    "website": "https://github.com/solvosci/slv-manufacture",
    "depends": ["mrp"],
    "data":[
        "views/ir_action_server.xml"
    ],
    "installable": True,
}
