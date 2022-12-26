# © 2022 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html

from odoo import models, fields, api

class FCDWeightScaleLog(models.Model):
    _name = 'fcd.weight.scale.log'
    _description = 'Scale Weight Log'

    name = fields.Char(compute="_compute_name" , store=True)
    date = fields.Datetime()
    weight_quantity = fields.Float()
    quantity = fields.Float()
    checkpoint_id = fields.Many2one('fcd.checkpoint')
    input_product_id = fields.Many2one('product.product')
    output_product_id = fields.Many2one('product.product')
    stock_move_id = fields.Many2one('stock.move')
    production_id = fields.Many2one('mrp.production')
    secondary_uom_id = fields.Many2one('product.secondary.unit')
    purchase_order_id = fields.Many2one('purchase.order', related='stock_move_id.purchase_line_id.order_id', store=True)
    fcd_document_line_id = fields.Many2one('fcd.document.line', related='stock_move_id.fcd_document_line_id', store=True)


    @api.depends("purchase_order_id.name", "input_product_id.name")
    def _compute_name(self):
        for record in self:
            record.name = record.purchase_order_id.name + "-" + record.input_product_id.name

    @api.model
    def create(self, vals):
        new_log = super().create(vals)
        self.packaging(new_log)
        return new_log

    def create_mrp_production(self, log_id):
        product_id = log_id.output_product_id
        stock_move_id = log_id.stock_move_id
        company_id = self.env.company
        location_src_id = stock_move_id.location_dest_id
        location_dest_id = self.env['stock.location'].search([('usage', '=', 'production'), ('company_id', '=', company_id.id)])

        lot_id = self.env['stock.production.lot'].search([
            ('name', '=', stock_move_id.fcd_document_line_id.lot_id.name),
            ('product_id', '=', product_id.id)
        ])
        if not lot_id:
            lot_id = self.env['stock.production.lot'].create({
                'name': stock_move_id.fcd_document_line_id.lot_id.name,
                'product_id': product_id.id,
                'company_id': company_id.id,
                'fcd_origin_lot_id': stock_move_id.fcd_document_line_id.lot_id.id,
            })

        # Company_id la del usuario checkpoint
        mrp_production_id = self.env['mrp.production'].create({
            'product_id': product_id.id,
            'product_uom_id': product_id.uom_id.id,
            'product_qty': log_id.quantity,
            'qty_producing': log_id.quantity,
            'qty_produced': log_id.quantity,
            'location_src_id': location_src_id.id,
            'location_dest_id': location_dest_id.id,
            'lot_producing_id': lot_id.id
        })

        raw_material_move_id = self.env['stock.move'].create({
            'name': stock_move_id.product_id.partner_ref,
            'product_id': stock_move_id.product_id.id,
            'product_uom': stock_move_id.product_id.uom_id.id,
            'product_uom_qty': log_id.quantity,
            'quantity_done': log_id.quantity,
            'raw_material_production_id': mrp_production_id.id,
            'location_id': location_src_id.id,
            'location_dest_id': location_dest_id.id,
        })

        mrp_production_id.action_confirm()

        finished_move_id = self.env['stock.move'].create({
            'name': product_id.partner_ref,
            'product_id': product_id.id,
            'product_uom': product_id.uom_id.id,
            'product_uom_qty': log_id.quantity,
            'quantity_done': log_id.quantity,
            'production_id': mrp_production_id.id,
            'location_id': location_dest_id.id,
            'location_dest_id': location_src_id.id,
            'state': 'done',
        })

        secondary_uom_id = log_id.input_product_id.production_secondary_uom_id

        raw_material_move_id.move_line_ids.write({
            'lot_id': stock_move_id.fcd_document_line_id.lot_id.id,
            'secondary_uom_id': secondary_uom_id.id,
            'secondary_uom_qty': 1,
            'state': 'done',
        })

        finished_move_id.move_line_ids.write({
            'lot_id': lot_id.id,
            'secondary_uom_id': log_id.secondary_uom_id.id,
            'secondary_uom_qty': 1,
        })
        mrp_production_id.button_mark_done()

        return mrp_production_id

    def packaging(self, log_id):
        #Update Weight and increase secondary unit
        move_id = log_id.stock_move_id
        move_extra_id = False
        purchase_line_id = move_id.purchase_line_id

        # If exists more than 1 move
        if len(purchase_line_id.move_ids) > 1:
            move_extra_id = purchase_line_id.move_ids.filtered(lambda x: x.state == "assigned")

        secondary_uom_id = move_id.product_id.production_secondary_uom_id

        # ctx = self._context.copy()
        # ctx.update({"fcd_weight_scale_mrp": True})

        move_id.write({
            "secondary_uom_id": secondary_uom_id.id,
        })
        move_id.move_line_ids.write({
            "qty_done": move_id.move_line_ids.qty_done + log_id.quantity,
            "secondary_uom_id": secondary_uom_id.id,
        })


        if move_id.picking_id.state != 'done':
            move_id.move_line_ids.write({
                "secondary_uom_qty": float(0),
        })
        move_id.move_line_ids.write({
            "secondary_uom_qty": move_id.move_line_ids.secondary_uom_qty + float(1),
        })

        if move_extra_id:
            if log_id.quantity >= move_extra_id.product_uom_qty:
                if len(move_extra_id.picking_id.move_ids_without_package) == 1:
                    move_extra_id.picking_id.unlink()
                else:
                    move_extra_id.write({
                        'state': 'draft'
                    })
                    move_extra_id.unlink()
            else:
                move_extra_id.write({
                    "product_uom_qty": move_extra_id.product_uom_qty - log_id.quantity
                })

        #Validate stock picking only if first time
        picking_id = move_id.picking_id
        if picking_id.state != "done":
            move_id.move_line_ids.write({
                "lot_id": move_id.fcd_document_line_id.lot_id.id,
                "expiration_date": move_id.fcd_document_line_id.fcd_document_id.expiration_date
            })
            picking_id.action_confirm()
            picking_id.action_assign()
            picking_id._action_done()

        production_id = self.create_mrp_production(log_id)

        #Create Log Modificar el vals dependiendo de si ya hay o no un movimiento del mismo producto
        log_id.write({
            'production_id': production_id.id,
        })

    def generate_qr(self):
        qr_code="EmpresaNombre: %s%%0AEmpresaDireccion: %s%%0AEmpresaPoblacion: %s %s%%0AEmpresaNRS: %s%%0AEmpresaAlmacen: %s%%0AProductoDenomComercial: %s%%0AProductoNombreCientifico: %s%%0AProductoFAO: %s%%0AProductoElaboracion: %s%%0AProductoElaboracionNotas: %s%%0AProductoCodAlfa3: %s%%0AProductoNLote: %s%%0AProductoArtePesca: %s%%0AProductoMetodoProd: %s%%0AProductoZona: %s%%0AProductoSubZona: %s%%0AProductoBuque: %s%%0AProductoMatricula: %s%%0AProductoArtes: %s%%0AFechaEnvasado: %s%%0AFechaCaducidad: %s%%0APesoKg: %s%%0AProductoPaisOrigen: %s" % (
            self.env.company.name,
            self.purchase_order_id.partner_id.name,
            self.purchase_order_id.partner_id.zip,
            self.purchase_order_id.partner_id.city,
            "???",
            self.purchase_order_id.picking_type_id.warehouse_id.name,
            self.output_product_id.name,
            self.output_product_id.scientific_name,
            self.fcd_document_line_id.fcd_document_id.fao,
            self.fcd_document_line_id.fcd_document_id.presentation_id.name,
            self.fcd_document_line_id.fcd_document_id.presentation_id.name,
            "???",
            self.fcd_document_line_id.fcd_document_id.name,
            self.fcd_document_line_id.fcd_document_id.fishing_gear_id.name,
            self.fcd_document_line_id.fcd_document_id.production_method_id.name,
            self.fcd_document_line_id.fcd_document_id.fao_zone_id.name,
            self.fcd_document_line_id.fcd_document_id.subzone_id.name,
            self.fcd_document_line_id.fcd_document_id.ship_id.name,
            self.fcd_document_line_id.fcd_document_id.ship_id.license_plate,
            "???",
            self.fcd_document_line_id.fcd_document_id.packaging_date,
            self.fcd_document_line_id.fcd_document_id.expiration_date,
            self.quantity,
            self.fcd_document_line_id.fcd_document_id.country_id.name,
        )
        return qr_code

    def generate_barcode(self):
        qty = str(self.quantity / 1000).replace('.', '')[:6]
        ean13 = self.fcd_document_line_id.purchase_order_line_id.product_id.ean13 if self.fcd_document_line_id.purchase_order_line_id.product_id.ean13 else "0000000000000"
        date = self.date.strftime("%y%m%d")
        lot = self.fcd_document_line_id.lot_id.name

        return '(01)%s(3102)%s(17)%s(10)%s' % (ean13, qty, date, lot)
