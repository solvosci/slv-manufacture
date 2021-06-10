# © 2021 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html
{
    "name": "Manufacturing data control: review gross weight of last wout",
    "summary": """
        Review gross weight of last wout:
        modify the gross weight of the last wout of each employee 
        with the gross weight calculated from the net weight 
        multiplied by the yield percentage of that day for that employee
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
        'data/ir_config_parameter.xml',
        'data/ir_cron.xml',
        'views/mdc_config_settings.xml',
    ],
    'installable': True,
}
