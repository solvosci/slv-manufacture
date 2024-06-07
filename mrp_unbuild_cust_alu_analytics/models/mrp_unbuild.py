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
    analytic_ids = fields.One2many(
        comodel_name="qc.inspection",
        inverse_name="unbuild_id",
        string="Analytics",
        copy=False
    )
    shift_stop_time = fields.Float(compute="_compute_shift_stop_time", store=True)

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id and self.process_type_id:
            self.bom_id = self.product_id.product_tmpl_id.bom_ids.filtered(lambda r: r.process_type_id == self.process_type_id)[0]
        else:
            super(MrpUnbuild, self)._onchange_product_id()

    @api.onchange('bom_id')
    def _onchange_bom_id(self):
        if self.bom_id:
            self.product_uom_id = self.bom_id.product_uom_id.id
        else:
            self.product_uom_id = False

    @api.onchange("incidence_ids")
    def _onchange_incidences_ids(self):
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

    @api.depends('incidence_ids', 'incidence_ids.duration')
    def _compute_shift_stop_time(self):
        for record in self:
            if record.incidence_ids:
                record.shift_stop_time = sum(record.incidence_ids.mapped('duration'))
            else:
                record.shift_stop_time = 0

    def _read_qc_inspection_xml(self):
        logger = logging.getLogger(__name__)
        path = self.env.company.xml_analytic_path   # TODO make it available to multi-company

        if not path:
            raise UserError(_("XML Analytic Path not defined"))

        # Find the folder and create if not exists
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
                        if attr['children'][0]['text'] == 'Código Material':
                            rel_unbuild_product_name = attr['children'][1]['text']
                    for analytic in data['children'][0]['children'][2]['children'][0]['children'][1]['children']:
                        for element in analytic['children']:
                            if element['attributes']:
                                if element['attributes']['StatType'] == 'Reported':
                                    if element['attributes']['CalibrationStatus'] == 'UnderRange':
                                        analytics.append({
                                            analytic['attributes']['ElementName']: "<" + element['children'][0]['text']
                                        })
                                    else:
                                        analytics.append({
                                            analytic['attributes']['ElementName']: element['children'][0]['text']
                                        })

                    #Process xml data
                    if unbuild_id:
                        if rel_unbuild_product_name:
                            rel_unbuild_product_id = unbuild_id.bom_line_ids.product_id.filtered(lambda x: x.default_code == rel_unbuild_product_name)
                            rel_unbuild_product_id = rel_unbuild_product_id[0].id if rel_unbuild_product_id else False
                        qc_inspection_id = self.env['qc.inspection'].create({
                            'name': "Inspection/%s" % (unbuild_id.name),
                            'unbuild_id': unbuild_id.id,
                            'test': self.env.ref('mrp_unbuild_cust_alu_analytics.qc_test_1').id,
                            'rel_unbuild_product_id': rel_unbuild_product_id,
                        })

                        qc_inspection_id.inspection_lines.unlink()
                        qc_inspection_id.inspection_lines = qc_inspection_id._prepare_inspection_lines(qc_inspection_id.test)
                        for inspection_line in qc_inspection_id.inspection_lines:
                            inspection_name = inspection_line.name
                            for item in analytics:
                                if inspection_name in item:
                                    if item[inspection_name][0] == '<':
                                        inspection_line.minor = True
                                        item[inspection_name] = item[inspection_name].split("<")[1]
                                    inspection_line.quantitative_value = float(item[inspection_name]) if float(item[inspection_name]) > 0 else float(item[inspection_name]) * -1
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
                        # When unbuild is not found, there are two possibilities:
                        # - No name found => it's a test analytic, so it should
                        #   be marked as processed, like a right one
                        # - Incorrect unbuild name => it should be kept as
                        #   unprocessed, so external users can check it and fix the problem
                        # TODO os.rename reuse => move to a function
                        if not unbuild_name:
                            os.rename("%s/%s" % (path, file), os.path.join(processed_folder_path + '/' + file))
                            logger.warning(
                                "Analytic file <%s> with no unbuild name moved to processed folder", file
                            )
                        else:
                            logger.error(
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
