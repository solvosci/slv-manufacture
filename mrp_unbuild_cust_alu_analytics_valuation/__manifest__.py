# © 2024 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html
{
    "name": "Mrp Unbuild Cust Alu Analytics - valuation link",
    "summary": """
        Link Mrp Unbuild Cust Alu Analytics to Stock Valuation MRP
    """,
    "author": "Solvos",
    "license": "LGPL-3",
    "version": "13.0.1.0.1",
    "category": "Manufacturing",
    "website": "https://github.com/solvosci/slv-manufacture",
    "depends": ["mrp_unbuild_cust_alu_analytics", "stock_valuation_mrp"],
    "data": [
        "views/product_template_views.xml",
        "views/product_product_views.xml",
        "views/product_pricelist_views.xml",
        "views/product_pricelist_item_views.xml",
        "views/mrp_unbuild_views.xml",
        "views/mrp_bom_views.xml",
        "views/mrp_bom_line_views.xml",
        "views/mrp_unbuild_process_type_views.xml",
        "views/mrp_unbuild_bom_totals_views.xml",
        "views/mrp_unbuild_views.xml",
    ],
    "post_init_hook": "post_init_hook",
    'installable': True,
}
