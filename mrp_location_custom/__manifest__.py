{
    'name': 'MRP - Custom source location per manufacturing order',
    'version': '15.0.1.0.0',
    'category': 'Manufacturing',
    'summary': 'Assigns a dedicated Pre-Production location to each manufacturing order.',
    'depends': ['mrp'],
    'data': [
        'views/stock_picking_type_views.xml',
        'views/mrp_production_views.xml',
    ],
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
}
