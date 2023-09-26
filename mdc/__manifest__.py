# © 2018 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0.html
{
    'name': "Manufacturing data control (MDC)",

    'summary': """
        Introduces Manufacturing data control (MDC) process in Odoo""",

    'description': """
        Manufacturing data control (MDC)
    """,

    'author': "Solvos",
    'website': "https://github.com/solvosci/slv-manufacture",

    'category': 'Manufacturing',
    'license': 'AGPL-3',
    'version': '16.0.1.0.0',

    'depends': [
        'hr_contract',
        'stock',
        'report_xlsx',
        'base_external_dbsource_sqlite'
    ],

    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv',
        'data/res_users.xml',
        'data/ir_config_parameter.xml',
        'data/ir_cron.xml',
        'data/structure_data.xml',
        'data/base_external_dbsource.xml',
        'views/data_views.xml',
        'views/hr_views.xml',
        'views/operation_views.xml',
        'views/structure_views.xml',
        'views/scale_views.xml',
        'views/mdc_config_settings.xml',
        'views/menuitem.xml',
        'views/templates.xml',
        'views/chkpoint_views.xml',
        'report/report_views.xml',
        'report/report_menuitem.xml',
    ],

    'demo': [
        'demo/demo.xml',
    ],

    'external_dependencies': {
        'python': [
            'websocket-client',
        ],
    },

    "application": True,
}