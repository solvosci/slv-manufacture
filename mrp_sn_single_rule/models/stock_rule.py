# © 2024 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See https://www.gnu.org/licenses/lgpl-3.0.html

from odoo import api, models


class StockRule(models.Model):
    _inherit = "stock.rule"

    @api.model
    def _run_manufacture(self, procurements):
        """
        Those procurements that belong to s/n products are splitted into single
        qty ones, so MOs that require only 1.0 qty will be created
        """
        new_procurements = []
        proc_obj = self.env["procurement.group"]
        for procurement, rule in procurements:
            if (
                procurement.product_id.tracking == "serial"
                and procurement.product_qty > 1.0
            ):
                for k in range(0, int(procurement.product_qty)):
                    new_procurements.append((
                        proc_obj.Procurement(
                            procurement.product_id,
                            1.0,
                            procurement.product_uom,
                            procurement.location_id,
                            procurement.name,
                            procurement.origin,
                            procurement.company_id,
                            procurement.values
                        ),
                        rule
                    ))
            else:
                new_procurements.append((procurement, rule))
        return super()._run_manufacture(new_procurements)
