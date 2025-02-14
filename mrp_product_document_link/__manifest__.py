# © 2025 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3 - See https://www.gnu.org/licenses/lgpl-3.0.html
{
    "name": "Manufacture Product Document Link",
    "summary": """
    Creates a shortcut to the product documents in the product form view from mrp.
    """,
    "author": "Solvos",
    "license": "AGPL-3",
    "version": "15.0.1.0.0",
    "category": "Manufacturing",
    "website": "https://github.com/solvosci/slv-manufacture",
    "depends": ["mrp", "document_url"],
    "data": [
        "views/mrp_production_views.xml",
    ]
}
