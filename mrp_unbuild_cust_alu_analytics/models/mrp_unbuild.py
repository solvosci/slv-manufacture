# © 2024 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3.0 (https://www.gnu.org/licenses/agpl-3.0.html)

from odoo import _, api, fields, models
from odoo.exceptions import UserError
import os
from lxml import etree
import logging

class MrpUnbuild(models.Model):
    _inherit = "mrp.unbuild"

    process_type_id = fields.Many2one('mrp.unbuild.process.type', string='Process type')
    incidence_ids = fields.One2many(
        comodel_name="mrp.unbuild.incidence",
        inverse_name="unbuild_id",
        string="Incidences",
    )
    analytic_ids = fields.Many2many(
        comodel_name="qc.inspection",
        string="Analytics",
        compute="compute_move_analytics",
        store=False
    )

    def compute_move_analytics(self):
        for record in self:
            analytics = self.env["qc.inspection"].search([("unbuild_id", "=", record.id)])
            record.analytic_ids = analytics

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id and self.process_type_id:
            self.bom_id = self.product_id.product_tmpl_id.bom_ids.filtered(lambda r: r.process_type_id == self.process_type_id)
        else:
            super(MrpUnbuild, self)._onchange_product_id()

    @api.onchange('bom_id')
    def _onchange_bom_id(self):
        if self.bom_id:
            self.product_uom_id = self.bom_id.product_uom_id.id
        else:
            self.product_uom_id = False

    @api.constrains('bom_quants_ids')
    def _contrains_bom_quants_ids(self):
        total_product_qty = sum(self.bom_quants_total_ids.mapped('total_qty'))
        self.product_qty = total_product_qty if total_product_qty > 0 else 1

    @api.constrains("incidence_ids")
    def _constrains_incidences_ids(self):
        if self.incidence_ids:
            self.shift_stop_time = sum(self.incidence_ids.mapped('duration'))
        else:
            self.shift_stop_time = 0

    @api.onchange("product_id", "process_type_id")
    def _onchange_product_id_process_type_id(self):
        for record in self:
            domain_bom_id = [
                "&",
                ("process_type_id", "=", record.process_type_id.id),
                ("product_tmpl_id", "=", record.product_id.product_tmpl_id.id)
            ]
            domain_product_id = [
                ("process_type_ids", "=", record.process_type_id.id),
            ]
        return {"domain": {"bom_id": domain_bom_id, "product_id": domain_product_id}}

    def read_qc_inspection_xml(self):
        # Find the folder and create if not exists
        path = self.env.company.xml_analytic_path   # TODO make it available to multi-company
        logger = logging.getLogger(__name__)
        if not path:
            raise UserError(_("XML Analytic Path not defined"))
        folder_path = os.path.join(path)
        processed_folder_path = os.path.join(path, 'processed')
        if not os.path.exists(folder_path):
            try:
                os.makedirs(folder_path)
                logger.info(
                    "Created folder on %s", folder_path
                )
            except OSError as e:
                raise UserError(_("Can't create folder")) from e

        if not os.path.exists(processed_folder_path):
            try:
                os.makedirs(processed_folder_path)
                logger.info(
                    "Created folder on %s", processed_folder_path
                )
            except OSError as e:
                raise UserError(_("Can't create folder")) from e

        files = os.listdir(folder_path)
        files.remove(processed_folder_path.split("/")[-1])
        if files:
            for file in files:
                unbuild_id = self.env['mrp.unbuild']
                unbuild_name = ""
                if file.endswith('.xml'):
                    # Get xml data
                    tree = etree.parse(folder_path + '/' + file)
                    root = tree.getroot()
                    data = self.get_element_and_children_data(root)
                    analytics = []
                    for attr in data['children'][0]['children'][0]['children']:
                        if attr['children'][0]['text'] == 'Proceso':
                            unbuild_id = unbuild_id.search([('name', '=', attr['children'][1]['text'])])
                            unbuild_name = attr['children'][1]['text']
                    for analytic in data['children'][0]['children'][2]['children'][0]['children'][1]['children']:
                        for element in analytic['children']:
                            if element['attributes']:
                                if element['attributes']['StatType'] == 'Mean':
                                    analytics.append({
                                        analytic['attributes']['ElementName']: float(element['children'][0]['text'])
                                    })

                    #Process xml data
                    if unbuild_id:
                        if unbuild_id.state == 'done':
                            move_id = False
                            move_line_ids = unbuild_id.produce_line_ids.move_line_ids
                            for move_line in move_line_ids.move_id:
                                if move_line.location_dest_id.usage == "production":
                                    move_id = move_line
                                    break

                            qc_inspection_id = self.env['qc.inspection'].create({
                                'name': "Inspection/%s" % (unbuild_id.name),
                                'unbuild_id': unbuild_id.id,
                                'object_id': "stock.move,%d" % move_id.id,
                                'test': self.env.ref('mrp_unbuild_cust_alu_analytics.qc_test_1').id,
                            })

                            qc_inspection_id.inspection_lines.unlink()
                            qc_inspection_id.inspection_lines = qc_inspection_id._prepare_inspection_lines(qc_inspection_id.test)
                            for inspection_line in qc_inspection_id.inspection_lines:
                                inspection_name = inspection_line.name
                                for item in analytics:
                                    if inspection_name in item:
                                        inspection_line.quantitative_value = item[inspection_name] if item[inspection_name] > 0 else item[inspection_name] * -1
                                        break
                                logger.info(
                                    "Added Analytics for mrp ubuild: %s", unbuild_id.name
                                )
                                qc_inspection_id.action_todo()
                                qc_inspection_id.action_confirm()
                                logger.info(
                                    "Confirmed Inspection %s for mrp ubuild: %s", qc_inspection_id.name, unbuild_id.name
                                )
                            # Move file to processed folder
                            os.rename("%s/%s" % (path, file), os.path.join(processed_folder_path + '/' + file))
                        else:
                            logger.info(
                                "Unbuild with name: %s, is not done yet", unbuild_id.name
                            )
                    else:
                        logger.info(
                            "Can't find unbuild with name: <%s>", unbuild_name
                        )


    def get_element_and_children_data(self, element):
        data = {
            'tag': element.tag,
            'text': element.text,
            'attributes': element.attrib,
            'children': []
        }
        for child in element:
            child_data = self.get_element_and_children_data(child)
            data['children'].append(child_data)
        return data
