# © 2024 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (https://www.gnu.org/licenses/lgpl-3.0.html)

from odoo import _, models, fields
from odoo.exceptions import ValidationError


class MrpUnbuild(models.Model):
    _inherit = "mrp.unbuild"

    qc_inspection_ids = fields.One2many('qc.inspection', 'mrp_unbuild_id', string='Quality Inspections')
    
    # def create(self, vals):
    #     # Call the original create method
    #     res = super(YourModelInheriting, self).create(vals)

    #     # Add your custom code here to extend the create method

    #     return res