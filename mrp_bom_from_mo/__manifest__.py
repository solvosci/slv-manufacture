# © 2026 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See https://www.gnu.org/licenses/lgpl-3.0.html

{
    "name": "MRP - Create Bill of Materials from Manufacturing Order",
    "summary": "Generate a Bill of Materials from the actual data of a done Manufacturing Order",
    "version": "15.0.1.0.0",
    "category": "Manufacturing",
    "author": "Solvos",
    "website": "https://github.com/solvosci/slv-manufacture",
    "license": "LGPL-3",
    "depends": ["mrp"],
    "data": [
        "security/ir.model.access.csv",
        "views/mrp_production_views.xml",
        "wizards/mrp_bom_from_mo_wizard_views.xml",
    ],
    "installable": True,
}
