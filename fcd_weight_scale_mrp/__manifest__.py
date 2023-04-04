# © 2022 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html
{
    'name': "FCD Weight Scale MRP",
    'summary': """
        Weight module to package lots 
    """,
    'author': "Solvos",
    'website': "http://www.solvos.com",
    'category': 'Weight',
    'version': '14.0.1.3.0',
    'depends': [
        "mrp",
        "fcd_purchase_order",
        "purchase_order_action_confirm_multi",
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/res_partner.xml',
        'data/res_users.xml',
        'data/fcd_weight_scale.xml',
        'data/fcd_checkpoint.xml',
        'views/assets.xml',
        'views/fcd_checkpoint_views_portal.xml',
        'views/fcd_checkpoint_views.xml',
        'views/fcd_weight_scale_mrp_menu.xml',
        'views/fcd_weight_scale_log_views.xml',
        'views/fcd_weight_scale.xml',
        'views/product_views.xml',
        'views/purchase_order_views.xml',
        'views/stock_move.xml',
        'views/stock_picking_views.xml',
        'views/stock_move_line_views.xml',
        'views/fcd_document_line_views.xml',
        'views/res_config_settings.xml',
        'views/product_category_views.xml',
        'reports/fcd_weight_scale_tag_report.xml',
        'reports/fcd_weight_scale_tag_template.xml',
        'wizards/fcd_weight_scale_mrp_wizard_views.xml'
    ],
    'installable': True,
    'application': True,
}
