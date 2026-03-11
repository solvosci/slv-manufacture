# © 2026 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html
{
    "name": "MRP Workorder Last Instruction Point",
    "summary": """
        This add-on adds a field to the MRP Workorder model to store
        the last technical instruction given to the operator in that workorder.
    """,
    "author": "Solvos",
    "license": "LGPL-3",
    "version": "15.0.1.0.1",
    "category": "Manufacturing/Manufacturing",
    "website": "https://github.com/solvosci/slv-manufacture",
    "depends": ["mrp"],
    "data": [
        "security/ir.model.access.csv",
        "views/mrp_workorder_views.xml",
        "wizard/mrp_workorder_productivity_instruction_view.xml",
    ],
}
