# © 2021 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html
from random import randint

from odoo import _, fields, models
from odoo.exceptions import UserError


class MrpTag(models.Model):
    _name = "mrp.tag"
    _description = "MRP Tag"

    def get_default_color_value(self):
        return randint(1, 15)

    name = fields.Char(string="Name", required=True)
    color = fields.Integer(
        string="Color Index (0-15)",
        default=lambda self: self.get_default_color_value(),
    )
    active = fields.Boolean(default=True)

    def copy(self, default=None):
        raise UserError(_("Tag copy is disabled"))

    _sql_constraints = [
        ("name_uniq", "unique (name)", "Tag name already exists!"),
    ]
