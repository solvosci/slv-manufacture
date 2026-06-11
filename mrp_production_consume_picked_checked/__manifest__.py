# © 2026 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html
{
    "name": "MRP Production Consume Picked Checked",
    "summary": """
        When consuming raw materials in a manufacturing order, for
        a component that originally had a demand of 0.0, will automatically mark it as 'picked'
        to ensure it is processed as a real consumption instead of being canceled.
    """,
    "author": "Solvos",
    "license": "LGPL-3",
    "version": "17.0.1.0.0",
    "category": "Manufacturing",
    "website": "https://github.com/solvosci/slv-manufacture",
    "depends": ["mrp"],
    'installable': True,
}
