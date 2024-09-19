# © 2024 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html
{
    'name': 'Unbuild Done Message',
    'summary': '''
        Adds automatic notification when unbuilds are done.
    ''',
    'author': 'Solvos',
    'license': 'LGPL-3',
    'version': '13.0.1.0.0',
    "category": "Manufacturing",
    "website": "https://github.com/solvosci/slv-manufacture",
    'depends': ['mrp'],
    'data': [
        'data/mail_template_data.xml',
        'views/stock_warehouse_view.xml',
    ],
    'installable': True,
}
