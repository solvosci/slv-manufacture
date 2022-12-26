# © 2022 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html

from odoo import models, fields


class MRPProduction(models.Model):
    _inherit = "mrp.production"

    fcd_document_line_id = fields.Many2one('fcd.document.line')

    def button_mark_done(self):
        res = super(MRPProduction, self).button_mark_done()
        return res
