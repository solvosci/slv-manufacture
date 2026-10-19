# Copyright 2026 Solvos Consultoría Informática
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "MRP Workorder Timeline Week Load",
    "summary": """
        This addon glues the mrp_workorder_timeline module with the mrp_workcenter_employee module,
        allowing to display the week load in the timeline view of work orders.""",
    "version": "15.0.1.0.0",
    "category": "Manufacturing",
    "author": "Solvos",
    "license": "AGPL-3",
    "depends": ["mrp_workorder_timeline", "mrp_workcenter_employee"],
    "assets": {
        "web.assets_backend": [
            "mrp_workorder_timeline_week_load/static/src/scss/web_timeline.scss",
            "mrp_workorder_timeline_week_load/static/src/js/timeline_renderer.js",
            "mrp_workorder_timeline_week_load/static/src/js/timeline_controller.js",
        ],
    },
    "installable": True,
}
