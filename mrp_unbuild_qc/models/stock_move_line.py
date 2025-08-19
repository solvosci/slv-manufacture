# © 2021 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (https://www.gnu.org/licenses/lgpl-3.0.html)
import ast
from odoo import models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    def action_unbuild_quality_control(self):
        action = self.env["ir.actions.act_window"]._for_xml_id(
            'quality_control_oca.action_qc_inspection'
        )

        domain = 'stock.move,%s' % (self.move_id.id)

        ctx = ast.literal_eval(action.get("context"))
        ctx.update({
            'default_object_id': domain,
            'default_unbuild_id': self.move_id.unbuild_id.id,
            'mrp_unbuild': True,
        })

        action['context'] = ctx
        action['domain'] = [('object_id', '=', domain)]
        return action
