# © 2026 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html
{
    "name": "MRP Workorder Last Instruction Point",
    "summary": """
        Add to workcenters employee list that can be assigned to a workorder.
        This allows for better management of employees and their assignments
        to specific workcenters within the manufacturing process.
    """,
    "author": "Solvos",
    "license": "LGPL-3",
    "version": "15.0.1.0.0",
    "category": "Manufacturing/Manufacturing",
    "website": "https://github.com/solvosci/slv-manufacture",
    "depends": ["mrp", "hr"],
    "data": [
        "security/ir.model.access.csv",
        "views/mrp_workorder_views.xml",
        "views/mrp_workcenter_views.xml",
    ],
}
