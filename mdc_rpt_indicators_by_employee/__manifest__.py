# © 2020 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html
{
    "name": "Manufacturing data control: Report Indicators by Employee",
    "summary": """
        Adds Report Indicators by Employee with data:
            - employee
            - workstation
            - date
            - times in and times out of the day
            - total hours day
    """,
    "author": "Solvos",
    "license": "LGPL-3",
    "version": "11.0.1.0.0",
    "category": "Manufacturing",
    "website": "https://github.com/solvosci/manufacture",
    "depends": [
        'mdc'
    ],
    "data": [
        "security/ir.model.access.csv",
        "report/report_views.xml",
        "report/report_menuitem.xml",
    ],
    'installable': True,
}
