# © 2024 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html
{
    "name": "Add new standart hourly cost fields",
    "summary": """
        Link Mrp Unbuild Cust Alu Analytics to Stock Valuation MRP
    """,
    "author": "Solvos",
    "license": "LGPL-3",
    "version": "13.0.1.0.0",
    "category": "Manufacturing",
    "website": "https://github.com/solvosci/slv-manufacture",
    "depends": ["mrp_unbuild_cust_alu_analytics", "stock_valuation_mrp"],
    "data": [
        "views/mrp_unbuild_process_type_views.xml",
    ],
    'installable': True,
}
