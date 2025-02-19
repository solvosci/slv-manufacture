# © 2025 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See https://www.gnu.org/licenses/lgpl-3.0.html

from odoo import api, models


class ManufactureOrder(models.Model):
    _inherit = "mrp.production"

    def _assign_user_id_to_children(self):
        for mrp in self:
            for child in mrp._get_children():
                child.user_id = self.user_id
                child._assign_user_id_to_children()

    @api.model
    def create(self, vals):
        record = super().create(vals)
        for source in record._get_sources():
            record.user_id = source.user_id
        return record

    def write(self, vals):
        res = super().write(vals)
        if "user_id" in vals:
            self._assign_user_id_to_children()
        return res
