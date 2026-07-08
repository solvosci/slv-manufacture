# © 2026 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See https://www.gnu.org/licenses/lgpl-3.0.html

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class MrpBomFromMoWizard(models.TransientModel):
    _name = 'mrp.bom.from.mo.wizard'
    _description = 'Create Bill of Materials from Manufacturing Order'

    production_id = fields.Many2one(
        comodel_name='mrp.production',
        string='Manufacturing Order',
        required=True,
        readonly=True,
    )
    code = fields.Char(
        string='Bill of Materials Reference',
        required=True,
        help='Reference that will be set on the newly created Bill of '
             'Materials.',
    )
    log_in_chatter = fields.Boolean(default=False)

    def _prepare_bom_line_values(self):
        """Build the (0, 0, {...}) commands for the BoM components, based
        on the components actually consumed on the Manufacturing Order,
        proportionally recalculated for 1 normalized unit of product."""
        self.ensure_one()
        production = self.production_id
        qty_produced = production.qty_produced or production.product_qty

        consumed_by_product = {}
        for move in production.move_raw_ids.filtered(lambda m: m.state != 'cancel'):
            qty_done = move.quantity_done
            if not qty_done:
                continue
            data = consumed_by_product.setdefault(
                move.product_id, {'qty': 0.0, 'uom': move.product_uom}
            )
            data['qty'] += qty_done

        bom_line_values = []
        for product, data in consumed_by_product.items():
            component_qty = data['qty'] / qty_produced
            bom_line_values.append((0, 0, {
                'product_id': product.id,
                'product_qty': component_qty,
                'product_uom_id': data['uom'].id,
            }))
        return bom_line_values

    def _prepare_operation_values(self):
        self.ensure_one()
        operation_values = []
        for sequence, workorder in enumerate(self.production_id.workorder_ids, start=1):
            operation_values.append((0, 0, {
                'name': workorder.name,
                'workcenter_id': workorder.workcenter_id.id,
                'time_cycle_manual': workorder.duration_expected,
                'sequence': sequence,
            }))
        return operation_values

    def action_create_bom(self):
        self.ensure_one()
        production = self.production_id

        if not production.qty_produced:
            raise UserError(_(
                'The Bill of Materials cannot be generated because this '
                'Manufacturing Order has no produced quantity.'
            ))

        # Ensure new BoM is the priorized one
        current_bom_ids = production.product_id.product_tmpl_id.bom_ids
        lowest_seq = current_bom_ids and current_bom_ids[0].sequence or 1
        for current_bom in current_bom_ids:
            current_bom.sequence = current_bom.sequence + 10

        bom_vals = {
            'sequence': lowest_seq,
            'product_tmpl_id': production.product_id.product_tmpl_id.id,
            'product_qty': 1.0,
            'product_uom_id': production.product_uom_id.id,
            'type': 'normal',
            'code': self.code,
            'bom_line_ids': self._prepare_bom_line_values(),
            'operation_ids': self._prepare_operation_values(),
        }
        bom = self.env['mrp.bom'].create(bom_vals)        

        if self.log_in_chatter:
            bom.message_post(body=_(
                'This Bill of Materials was generated from Manufacturing '
                'Order %s.'
            ) % production.name)

            production.message_post(body=_(
                'Bill of Materials %s was created from this Manufacturing '
                'Order.'
            ) % bom.display_name)

        return {
            'name': _('Bill of Materials'),
            'type': 'ir.actions.act_window',
            'res_model': 'mrp.bom',
            'res_id': bom.id,
            'view_mode': 'form',
            'target': 'current',
        }
