# © 2022 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html

from odoo.exceptions import ValidationError
from odoo import models, api, _


class ProductSecondaryUnit(models.Model):
    _inherit = "product.secondary.unit"

    @api.model
    def create(self, values):
        if self.env['product.template'].browse(values['product_tmpl_id']).production_secondary_uom_id and values['factor'] == 0:
            raise ValidationError(_('Cannot create another secondary unit of measure with factor 0.00 !'))
        return super(ProductSecondaryUnit, self).create(values)

    def write(self, values):
        for record in self:
            if record.id == record.product_tmpl_id.production_secondary_uom_id.id:
                raise ValidationError(_('Cannot edit secondary unit of measure with factor 0.00 !'))
            if record.product_tmpl_id.production_secondary_uom_id and values['factor'] == 0:
                raise ValidationError(_('Cannot create another secondary unit of measure with factor 0.00 !'))
        super(ProductSecondaryUnit, self).write(values)

    def unlink(self):
        for record in self:
            if record.id == record.product_tmpl_id.production_secondary_uom_id.id:
                raise ValidationError(_('Cannot delete secondary unit of measure with factor 0.00 !'))
        super(ProductSecondaryUnit, self).unlink()
