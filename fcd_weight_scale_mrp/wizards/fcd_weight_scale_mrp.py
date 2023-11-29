# © 2023 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, _
from odoo.exceptions import ValidationError


class FCDWeightScaleMRPWizard(models.TransientModel):
    _name = 'fcd.weight.scale.mrp.wizard'
    _description = 'fcd.weight.scale.mrp.wizard'

    purchase_line_id = fields.Many2one('purchase.order.line')

    def remove_last_weight_scale(self):
        if self.purchase_line_id.fcd_log_ids:
            log_id = self.purchase_line_id.fcd_log_ids[-1]

            # Create mrp.unbuild for mrp.production
            if log_id.production_id:
                production_id = log_id.production_id

                unbuild = self.env['mrp.unbuild'].new({
                    'lot_id': production_id.lot_producing_id.id,
                    'mo_id': production_id.id,
                    'location_id': production_id.location_dest_id.id,
                    'location_dest_id': production_id.location_src_id.id,
                    'company_id': production_id.company_id.id,
                })
                unbuild._onchange_mo_id()
                vals = unbuild._convert_to_write(unbuild._cache)
                unbuild_id = self.env['mrp.unbuild'].sudo().create(vals)
                unbuild_id.action_unbuild()

            # Rest quantity od stock move
            move_id = log_id.stock_move_id
            move_id.move_line_ids.write({
                "qty_done": move_id.move_line_ids.qty_done - log_id.quantity,
                "secondary_uom_qty": move_id.move_line_ids.secondary_uom_qty - float(1),
            })

            # Exist assigned move
            move_extra_id = self.purchase_line_id.move_ids.filtered(lambda x: x.state == "assigned")
            if move_extra_id:
                move_extra_id.write({
                    "product_uom_qty": self.purchase_line_id.product_qty - self.purchase_line_id.qty_received,
                })
                move_extra_id.move_line_ids.write({
                    "product_uom_qty": self.purchase_line_id.product_qty - self.purchase_line_id.qty_received,
                })
            elif self.purchase_line_id.qty_received < self.purchase_line_id.product_qty:
                # Exist picking but no exist assigned move
                if self.purchase_line_id.order_id.picking_ids.filtered(lambda x: x.state == "assigned"):
                    self.purchase_line_id.order_id.picking_ids.filtered(lambda x: x.state == "assigned").move_ids_without_package.create({
                        'name': self.purchase_line_id.product_id.display_name,
                        'product_id': self.purchase_line_id.product_id.id,
                        'purchase_line_id': self.purchase_line_id.id,
                        'product_uom_qty': self.purchase_line_id.product_qty - self.purchase_line_id.qty_received,
                        'product_uom': self.purchase_line_id.product_uom.id,
                        'secondary_uom_id': self.purchase_line_id.secondary_uom_id.id,
                        'state': 'assigned',
                        'picking_id': self.purchase_line_id.order_id.picking_ids.filtered(lambda x: x.state == "assigned").id,
                        'location_id': self.purchase_line_id.order_id.picking_ids.filtered(lambda x: x.state == "assigned").move_ids_without_package.location_id.id,
                        'location_dest_id': self.purchase_line_id.order_id.picking_ids.filtered(lambda x: x.state == "assigned").move_ids_without_package.location_dest_id.id,
                    })
                # Not exist picking
                else:
                    picking_id = self.purchase_line_id.order_id.picking_ids.create({
                        'picking_type_id': self.purchase_line_id.order_id.picking_type_id.id,
                        'partner_id': self.purchase_line_id.order_id.partner_id.id,
                        'user_id': False,
                        'date': self.purchase_line_id.order_id.date_order,
                        'origin': self.purchase_line_id.order_id.name,
                        'location_dest_id': self.purchase_line_id.order_id._get_destination_location(),
                        'location_id': self.purchase_line_id.order_id.partner_id.property_stock_supplier.id,
                        'company_id': self.env.company.id,
                        'state': 'assigned',
                    })
                    picking_id.move_ids_without_package.create({
                        'name': self.purchase_line_id.product_id.display_name,
                        'product_id': self.purchase_line_id.product_id.id,
                        'purchase_line_id': self.purchase_line_id.id,
                        'product_uom_qty': self.purchase_line_id.product_qty - self.purchase_line_id.qty_received,
                        'product_uom': self.purchase_line_id.product_uom.id,
                        'secondary_uom_id': self.purchase_line_id.secondary_uom_id.id,
                        'state': 'assigned',
                        'picking_id': picking_id.id,
                        'location_id': picking_id.location_id.id,
                        'location_dest_id': picking_id.location_dest_id.id,
                    })

            # Remove log
            log_id.unlink()
        else:
            raise ValidationError(_('There is no record of weighing in this order line'))
