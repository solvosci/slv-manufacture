# © 2022 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html

from odoo.exceptions import ValidationError
from odoo import models, api, _


class ProductSecondaryUnit(models.Model):
    _inherit = "product.secondary.unit"

    @api.model
    def unlink(self):
        if self.id == self.product_tmpl_id.production_secondary_uom_id.id:
            raise ValidationError(_('You should not unlink the secondary unit used on production!'))
        return super().unlink()