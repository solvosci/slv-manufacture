# © 2022 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html

from odoo import models, fields, api, _
from datetime import timedelta
import subprocess
import os
import logging

_logger = logging.getLogger(__name__)


class FCDWeightScaleLog(models.Model):
    _name = 'fcd.weight.scale.log'
    _description = 'Scale Weight Log'

    name = fields.Char(compute="_compute_name" , store=True)
    date = fields.Datetime()
    weight_quantity = fields.Float()
    quantity = fields.Float(digits="Product Unit of Measure")
    checkpoint_id = fields.Many2one('fcd.checkpoint')
    input_product_id = fields.Many2one('product.product')
    output_product_id = fields.Many2one('product.product')
    stock_move_id = fields.Many2one('stock.move')
    production_id = fields.Many2one('mrp.production')
    secondary_uom_id = fields.Many2one('product.secondary.unit')
    purchase_order_line_id = fields.Many2one('purchase.order.line', related='stock_move_id.purchase_line_id', store=True)
    purchase_order_id = fields.Many2one('purchase.order', related='stock_move_id.purchase_line_id.order_id', store=True)
    produced_partner_id = fields.Many2one('res.partner', related="purchase_order_id.picking_type_id.warehouse_id.partner_id", store=True)
    warehouse_id = fields.Many2one('stock.warehouse', related="purchase_order_id.picking_type_id.warehouse_id", store=True)
    fcd_document_line_id = fields.Many2one('fcd.document.line', related='stock_move_id.fcd_document_line_id', store=True)
    packaging_date = fields.Date()
    expiration_date = fields.Date(compute="_compute_expiration_date", store=True)
    pieces = fields.Integer()


    @api.depends("packaging_date")
    def _compute_expiration_date(self):
        for record in self:
            if record.output_product_id.fcd_expiration_days:
                record.expiration_date = (record.packaging_date + timedelta(days=record.output_product_id.fcd_expiration_days)).strftime('%Y-%m-%d')
            else:
                record.expiration_date = False

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
        qr_code="EmpresaNombre: %s%%0AEmpresaDireccion: %s%%0AEmpresaPoblacion: %s %s%%0AEmpresaNRS: %s%%0AEmpresaAlmacen: %s%%0AProductoDenomComercial: %s%%0AProductoNombreCientifico: %s%%0AProductoFAO: %s%%0AProductoElaboracion: %s%%0AProductoCodAlfa3: %s%%0AProductoNLote: %s%%0AProductoArtePesca: %s%%0AProductoMetodoProd: %s%%0AProductoZonaSubzona: %s%%0AProductoBuque: %s%%0AProductoMatricula: %s%%0AFechaEnvasado: %s%%0AFechaCaducidad: %s%%0APesoKg: %s" % (
            self.env.company.name,
            self.produced_partner_id.second_name_fcd or '',
            self.produced_partner_id.zip or '',
            self.produced_partner_id.city or '',
            self.fcd_document_line_id.fcd_document_id.sanity_reg or '',
            self.purchase_order_id.picking_type_id.warehouse_id.name or '',
            self.output_product_id.name or '',
            self.output_product_id.scientific_name or '',
            self.fcd_document_line_id.fcd_document_id.fao or '',
            self.fcd_document_line_id.fcd_document_id.presentation or '',
            self.fcd_document_line_id.fcd_document_id.presentation_code or '',
            self.fcd_document_line_id.lot_id.name or '',
            self.fcd_document_line_id.fcd_document_id.fishing_gear or '',
            self.fcd_document_line_id.fcd_document_id.production_method or '',
            self.fcd_document_line_id.fcd_document_id.fao_zone or '',
            self.fcd_document_line_id.fcd_document_id.ship or '',
            self.fcd_document_line_id.fcd_document_id.ship_license_plate or '',
            self.packaging_date or '',
            self.expiration_date or '',
            self.quantity,
        )
        return qr_code

    def generate_barcode_base(self):
        ean13 = self.fcd_document_line_id.purchase_order_line_id.product_id.ean13 if self.fcd_document_line_id.purchase_order_line_id.product_id.ean13 else "0000000000000"
        qty = '{:06.0f}'.format(self.quantity * 100)
        lot = self.fcd_document_line_id.lot_id.name

        return ean13, qty, lot

    def generate_barcode(self):
        ean13, qty, lot = self.generate_barcode_base()
        return '02%s\\x1D3102%s\\x1D10%s' % (ean13, qty, lot)

    def generate_barcode_text(self):
        ean13, qty, lot = self.generate_barcode_base()
        return '(02)%s(3102)%s(10)%s' % (ean13, qty, lot)

    def generate_report_tag_zpl(self):
        tag_fields = {
            'address': self.produced_partner_id.second_name_fcd,
            'address2': f'{self.produced_partner_id.phone} {self.produced_partner_id.city} ({self.produced_partner_id.state_id.name})',
            'shipper_street': self.produced_partner_id.street,
            'shipper_city': self.produced_partner_id.city,
            'shipper_street2': self.produced_partner_id.street2,
            'ship_name': self.fcd_document_line_id.fcd_document_id.ship if self.fcd_document_line_id.fcd_document_id.ship else '',
            'ship_license_plate': self.fcd_document_line_id.fcd_document_id.ship_license_plate if self.fcd_document_line_id.fcd_document_id.ship_license_plate else '',
            'sanitary_reg': self.fcd_document_line_id.fcd_document_id.sanity_reg if self.fcd_document_line_id.fcd_document_id.sanity_reg else '',
            'expiration_date': self.expiration_date.strftime('%d-%m-%Y') if self.expiration_date else '',
            'packaging_date': self.packaging_date.strftime('%d-%m-%Y') if self.packaging_date else '',
            'product_name': self.output_product_id.name,
            'product_scientific_name': self.output_product_id.scientific_name if self.output_product_id.scientific_name else '',
            'product_fao': self.output_product_id.fao if self.output_product_id.fao else '',
            'fao_zone': self.fcd_document_line_id.fcd_document_id.fao_zone if self.fcd_document_line_id.fcd_document_id.fao_zone else '',
            'production_method': self.fcd_document_line_id.fcd_document_id.production_method if self.fcd_document_line_id.fcd_document_id.production_method else '',
            'pieces': self.pieces,
            'quantity': self.quantity,
            'caliber': self.output_product_id.caliber if self.output_product_id.caliber else '',
            'fishing_gear': self.fcd_document_line_id.fcd_document_id.fishing_gear if self.fcd_document_line_id.fcd_document_id.fishing_gear else '',
            'fishing_gear2': '',
            'presentation': self.output_product_id.presentation_id.name if self.output_product_id.presentation_id.name else '',
            'lot': self.fcd_document_line_id.lot_id.name,
            'barcode': self.generate_barcode(),
            'barcode_text': self.generate_barcode_text(),
            'qr': self.generate_qr()
        }

        if len(tag_fields['ship_name']) > 23:
            tag_fields['ship_name'] = f'{tag_fields["ship_name"][0:23]}...'

        if len(tag_fields['product_scientific_name']) > 35:
            tag_fields['product_scientific_name'] = f'{tag_fields["product_scientific_name"][0:35]}...'
        if len(tag_fields['fao_zone']) > 64:
            tag_fields['fao_zone'] = f'{tag_fields["fao_zone"][0:64]}...'

        if len(tag_fields['fishing_gear']) > 29:
            tag_fields['fishing_gear2'] = tag_fields['fishing_gear'][28::]
            tag_fields['fishing_gear'] = tag_fields['fishing_gear'][0:28]

        if self.output_product_id.categ_id.get_fcd_type() == 'fish':
            tag_fields['type'] = _('Contains fish. May contain traces of crustaceans and/or molluscs.')
        elif self.output_product_id.categ_id.get_fcd_type() == 'crustaceans_sulphites':
            tag_fields['type'] = _('Contains crustaceans and sulfites. May contain traces of fish and/or molluscs.')
        elif self.output_product_id.categ_id.get_fcd_type() == 'molluscs':
            tag_fields['type'] = _('Contains mollusks. May contain traces of fish and/or crustaceans.')
        else:
            tag_fields['type'] = ''

        tag_fields['pieces_box'] = ''
        if tag_fields['pieces']:
            tag_fields['pieces_box'] = f'''
                ^FO290,400^A0R,20,20^FDPIEZAS:^FS
                ^FO275,470^A0R,45,55^FD{tag_fields['pieces']}^FS
            '''

        content_zpl = f'''
            ^XA

            ^FX líneas de la etiqueta
            ^FX ===================================

            ^FX --- Sección Superior Izquierda - líneas horizontales ---
            ^FO455,15^GB0,370,2^FS
            ^FO360,15^GB0,370,2^FS
            ^FO250,15^GB0,370,2^FS
            ^FX --- Sección Superior separador vertical - izquierda - centro ---
            ^FO180,385^GB370,0,2^FS
            ^FX Sección Superior Central - líneas horizontales ---
            ^FO430,385^GB0,540,2^FS
            ^FO330,385^GB0,540,2^FS
            ^FX Sección Superior Central- Pequeña línea vertical ---
            ^FO180,700^GB150,0,2^FS
            ^FX --- Sección Superior Izquierda- líneas QR ---
            ^FO220,925^GB0,300,2^FS
            ^FO220,925^GB330,0,2^FS
            ^FX --- Fin Sección Superior - Línea Horizontal ---
            ^FO180,15^GB0,1210,2^FS

            ^FX --- Sección Inferior Cajas ---
            ^FO15,15^GB120,1210,2^FS
            ^FO133,15^GB30,370,2^FS
            ^FO133,383^GB30,842,2^FS


            ^FX Texto y Datos
            ^FX ===================================
            ^CI28
            ^FX --- Título: Empresa y dirección ---
            ^FO520,25^A0R,28,28^FDCIGURRIA O CAMPO S.L.^FS
            ^FO490,25^A0R,20,20^FD{tag_fields['address']}^FS
            ^FO465,25^A0R,20,20^FD{tag_fields['address2']}^FS

            ^FX --- Expedidor ---
            ^FO420,25^A0R,20,20^FDEXPEDIDOR 1º:^FS
            ^FO420,155^A0R,20,20^FD{tag_fields['shipper_street']}^FS
            ^FO395,25^A0R,20,20^FDDIRECCIÓN:^FS
            ^FO395,125^A0R,20,20^FD{tag_fields['shipper_city']}^FS
            ^FO370,25^A0R,20,20^FDNº R.S.I.:^FS
            ^FO370,110^A0R,20,20^FD{tag_fields['shipper_street2']}^FS

            ^FX --- Buque y Sello ---
            ^FO260,30^GB90,200,2^FS
            ^FO260,240^GE90,130,2^FS
            ^FO320,40^A0R,20,20^FDEST.ELAB/BUQUE:^FS
            ^FX --- Nombre patido en 2 líneas (15 caracteres + 15 caracteres) ---
            ^FO300,40^A0R,15,15^FD{tag_fields['ship_name']}^FS
            ^FO280,40^A0R,15,15^FD{tag_fields['ship_license_plate']}^FS
            ^FO320,300^A0R,15,15^FDES^FS
            ^FO300,270^A0R,15,15^FD{tag_fields['sanitary_reg']}^FS
            ^FO280,300^A0R,15,15^FDCE^FS

            ^FX --- Fechas ---
            ^FO215,25^A0R,20,20^FDF.CADUCIDAD:^FS
            ^FO215,250^A0R,20,20^FD{tag_fields['expiration_date']}^FS
            ^FO190,25^A0R,20,20^FDF.ENVASADO:^FS
            ^FO190,250^A0R,20,20^FD{tag_fields['packaging_date']}^FS

            ^FX --- Denominación comercial del Producto ---
            ^FO530,400^A0R,20,20^FDDENOMINACIÓN COMERCIAL:^FS
            ^FO500,400^A0R,25,25^FD{tag_fields['product_name']}^FS
            ^FO465,400^A0R,20,20^FDNOMBRE CIENTÍFICO:^FS
            ^FO465,580^A0R,20,20^FD{tag_fields['product_scientific_name']}^FS
            ^FO440,400^A0R,20,20^FDFAO:^FS
            ^FO440,440^A0R,20,20^FD{tag_fields['product_fao']}^FS

            ^FX --- Zona y Subzona de Captura ---
            ^FO400,400^A0R,20,20^FDZONA Y SUBZONA DE CAPTURA:^FS
            ^FO375,400^A0R,18,18^FD{tag_fields['fao_zone']}^FS
            ^FO345,400^A0R,20,20^FDMÉTODO DE PRODUCCIÓN:^FS
            ^FO345,625^A0R,20,20^FD{tag_fields['production_method']}^FS

            ^FX --- PIEZAS Y PESO NETO ---
            {tag_fields['pieces_box']}
            ^FO225,400^A0R,20,20^FDPESO NETO (KG):^FS
            ^FO205,545^A0R,60,70^FD{tag_fields['quantity']}^FS

            ^FX --- Calibre, Arte de Pesca y Presentación ---
            ^FO300,720^A0R,20,20^FDCALIBRE:^FS
            ^FO300,800^A0R,20,20^FD{tag_fields['caliber']}^FS
            ^FO260,720^A0R,20,20^FDARTE DE PESCA:^FS
            ^FX --- Nombre patido en 2 líneas (15 caracteres + 15 caracteres) ---
            ^FO240,720^A0R,18,15^FD{tag_fields['fishing_gear']}^FS
            ^FO220,720^A0R,18,15^FD{tag_fields['fishing_gear2']}^FS
            ^FO190,720^A0R,20,20^FDPRESENTACIÓN:^FS
            ^FO190,860^A0R,20,20^FD{tag_fields['presentation']}^FS

            ^FX --- Método de Conservación y Trazas de Pesacado ---
            ^FO138,30^A0R,20,20^FDMetodo de conservacion entre 0ºC-5ºC^FS
            ^FO138,400^A0R,20,20^FD{tag_fields['type']}^FS

            ^FX --- LOTE ---
            ^FO230,960^A0R,20,20^FDLOTE:^FS
            ^FO230,1040^A0R,25,35^FD{tag_fields['lot']}^FS

            ^FX --- Código QR ---
            ^FO280,950^BQ,2,3^FD{tag_fields['qr']}^FS

            ^FX --- Código de Barras ---
            ^FO60,70^BY2,3,10^BCR,60,N,N,N^FD{tag_fields['barcode']}^FS
            ^FO25,360^A0R,20,30^FD{tag_fields['barcode_text']}^FS

            ^XZ
        '''

        # Store file
        content_zpl_bytes = content_zpl.encode('utf-8')
        file_name = f'tag_{self.id}.zpl'

        parent_folder = (_("/tmp/"))
        try:
            os.makedirs(parent_folder)
        except OSError:
            # In the case that the folders already exist
            pass
        path_tag = '%s%s' % (parent_folder, file_name)
        with open(path_tag, "wb") as file:
            file.write(content_zpl_bytes)

        # Send File To FTP
        comms = [f'''
            ftp -p -inv {self.checkpoint_id.printer_ip} {self.checkpoint_id.printer_port} <<EOF
            user itadmin pass
            put {path_tag} pr1
            bye
            EOF
        ''']

        err = False
        try:
            res = subprocess.run(comms, shell=True, capture_output=True, text=True, timeout=5)
            _logger.warning(res.stderr)
            if "Login incorrect" in res.stderr:
                _logger.warning("Error: Login incorrect.")
                err = {"error": "Login incorrect"}
            elif "No such file or directory" in res.stderr:
                _logger.warning("Error: No such file or directory.")
                err = {"error": "No such file or directory"}
            elif "No route to host" in res.stderr:
                _logger.warning("Error: No route to host.")
                err = {"error": _("Printer Not Conected")}
        except subprocess.TimeoutExpired:
            _logger.warning("Error: Printer Not Conected.")
            err = {"error": _("Printer Not Conected")}

        # Remove file
        if os.path.exists(path_tag):
            os.remove(path_tag)
        else:
            _logger.warning("File not exist")

        if err:
            return err
        else:
            return {'ret': True}
