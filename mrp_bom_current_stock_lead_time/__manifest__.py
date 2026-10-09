# Copyright 2018 Camptocamp SA
# Copyright 2017-20 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "MRP BoM Current Stock Lead Time",
    "summary": "Add lead time to the current stock report, based on the "
            "stock available in the source location. "
            "It also adds the routes of the components",
    "version": "15.0.1.0.0",
    "category": "Manufacture",
    "website": "https://github.com/solvosci/slv-manufacture",
    "author": "Solvos",
    "license": "AGPL-3",
    "depends": ["mrp_bom_current_stock"],
    "data": [
        "reports/report_mrpcurrentstock.xml",
        "views/bom_route_current_stock_view.xml",
    ],
}
