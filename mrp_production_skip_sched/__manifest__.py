# © 2023 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See https://www.gnu.org/licenses/lgpl-3.0.html
{
    "name": "MRP Production - prevent trigger scheduler",
    "summary": """
    Prevents thas sheduler is triggered when a production is
    confirmed or changed once confirmed.
    Scheduler cron or manual execution should do the trick
    instead
    """,
    "author": "Solvos",
    "license": "LGPL-3",
    "version": "15.0.1.0.0",
    "category": "Manufacturing",
    "website": "https://github.com/solvosci/slv-manufacture",
    "depends": ["mrp"],
    "installable": True,
}
