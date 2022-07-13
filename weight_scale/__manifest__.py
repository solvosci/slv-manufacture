# © 2022 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html
{
    'name': "Weight Scale Packaging",
    'summary': """
        Weight module to package lots 
    """,
    'author': "Solvos",
    'website': "http://www.solvos.com",
    'category': 'Weight',
    'version': '14.0.1.0.0',
    'depends': ['base'],
    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv',
        'data/chkpointUser.xml',
        'views/weight_scale_menu.xml',
        'views/chkpoint_views.xml',
        'views/lot_views.xml',
    ],
    'installable': True,
    'application': True,
}
