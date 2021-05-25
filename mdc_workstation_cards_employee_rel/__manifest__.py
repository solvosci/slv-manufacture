# © 2021 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html
{
    "name": "Manufacturing data control: Add employee to workstation cards",
    "summary": """
        To able to put employee in a workstation card.
		And when a employee changes his workstation 
		then changes the workstation of all workstation cards 
		of this employee with the new workstation of the employee.
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
        "views/operation_views.xml",
    ],
    "post_init_hook": "post_init_hook",
    'installable': True,
}
