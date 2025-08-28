# # © 2025 Solvos Consultoría Informática (<http://www.solvos.es>)
# # License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html
from odoo import models, api, _, fields
from datetime import datetime
from lxml import etree as ET
from pathlib import Path
from odoo.addons.base.models.res_partner import _tz_get
import pytz
import traceback
import logging
import re
import ftplib


class MaintenanceEquipment(models.Model):
    _inherit = 'maintenance.equipment'

    mdc_xml_import_active = fields.Boolean(
        string="XML File Import Active",
        default=False,
    )
    mdc_xml_weight_in_path = fields.Char(
        string="XML Input Folder Path",
        help="Path to the folder where unprocessed XML files are placed."
    )
    mdc_xml_weight_processed_path = fields.Char(
        string="XML Processed Folder Path",
        help="Path to the folder where processed XML files are moved."
    )
    # FTP connection settings
    requires_ftp = fields.Boolean(
        string="Requires FTP Connection",
        default=False,
        )
    ftp_host = fields.Char(string="IP/URL")
    ftp_port = fields.Char(string="Port")
    ftp_user = fields.Char(string="Username")
    ftp_password = fields.Char(string="Password")
    ftp_folder = fields.Char(string="Folder")

    mdc_timezone = fields.Selection(
        selection=_tz_get,
        string="Timezone",
        default=lambda self: self.env.user.tz or 'UTC',
        help="Timezone for the equipment."
    )

    @api.model
    def _cron_import_xml_weight(self):
        logger = logging.getLogger(__name__)
        errors = []
        for record in self.env['maintenance.equipment'].search([
                    ('mdc_xml_import_active', '=', True),
                ]):
            if record.requires_ftp:
                try:
                    self._download_files_from_ftp(record)
                except Exception as e:
                    logger.error("Error downloading files from FTP: %s", e)
                    errors.append({
                        'company_id': record.company_id and record.company_id.id or False,
                        'equipment_id': record.id,
                        'file_name': None,
                        'error_message': (_("Error downloading files from FTP: %s", e)),
                        'traceback': traceback.format_exc(),
                    })
            in_path = Path(record.mdc_xml_weight_in_path)
            processed_path = Path(record.mdc_xml_weight_processed_path)

            try:
                in_path.mkdir(parents=True, exist_ok=True)
                processed_path.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                logger.error("Can't create folders: %s", e)
                errors.append({
                    'company_id': record.company_id and record.company_id.id or False,
                    'equipment_id': record.id,
                    'file_name': None,
                    'error_message': (_("Folder creation failed: %s",e)),
                    'traceback': traceback.format_exc(),
                })
                continue

            try:
                files = [f for f in in_path.iterdir() if f.is_file()]
            except Exception as e:
                logger.error("Error listing files: %s", e)
                errors.append({
                    'company_id': record.company_id and record.company_id.id or False,
                    'equipment_id': record.id,
                    'file_name': None,
                    'error_message': (_("Listing files failed: %s",e)),
                    'traceback': traceback.format_exc(),
                })
                continue

            if not files:
                logger.info("No files to process in %s", in_path)
                continue

            for file in files:
                if not file.name.lower().endswith('.xml'):
                    logger.warning("Skipping non-XML file: %s", file.name)
                    continue
                try:
                    self._process_xml_file(file, processed_path, record)
                except Exception as e:
                    logger.error("Error processing file %s: %s", file.name, e)
                    errors.append({
                        'company_id': record.company_id and record.company_id.id or False,
                        'equipment_id': record.id,
                        'file_name': file.name,
                        'error_message': (_("Processing failed: %s",e)),
                        'traceback': traceback.format_exc(),
                    })

        if errors:
            error_model = self.env['mdc.weight.record.error'].sudo()
            created_errors = error_model.create(errors)
            created_errors.action_send_mail()
# ********** Getters for XML data extraction ***********
    def get_statvalue_by_id(self,stat_id, unit=None, root=None, nsmap=None):
        query = f'.//wpt:Statvalue[@id="{stat_id}"]'
        if unit:
            query += f'[wpt:Unit[@id="{unit}"]]'
        nodes = root.xpath(query, namespaces=nsmap)
        if nodes:
            val = nodes[0].find("wpt:Value", namespaces=nsmap)
            return val.text if val is not None else None
        return None

    def get_text_from(self,tag_name, root=None, nsmap=None):
        nodes = root.xpath(f'.//wpt:{tag_name}', namespaces=nsmap)
        return nodes[0].text.strip() if nodes and nodes[0].text else None
# ***********************

    def _connect_ftp(self,record):
        """Connect to the FTP server using the provided settings."""
        logger = logging.getLogger(__name__)
        try:
            ftp = ftplib.FTP()
            ftp.connect(record.ftp_host, int(record.ftp_port))
            ftp.login(record.ftp_user, record.ftp_password)
            logger.info("Connected to FTP server: %s", record.ftp_host)
            return ftp
        except Exception as e:
            logger.error("FTP connection failed: %s", e)
            raise Exception(_("FTP connection failed: %s", e))

    def _download_files_from_ftp(self, record):
        logger = logging.getLogger(__name__)
        try:
            ftp = self._connect_ftp(record)
        except Exception as e:
            logger.error("FTP connection failed: %s", e)
            raise Exception(_("FTP connection failed: %s", e))
        try:
            if record.ftp_folder:
                try:
                    ftp.cwd(record.ftp_folder)
                except Exception as e:
                    logger.error("Failed to change directory to %s: %s", record.ftp_folder, e)
                    raise Exception(_("Failed to change directory to %s: %s", record.ftp_folder, e))
            files = ftp.nlst()
            for file_name in files:
                if not file_name.lower().endswith('.xml'):
                    logger.warning("Skipping non-XML file: %s", file_name)
                    continue
                local_file_path = Path(record.mdc_xml_weight_in_path) / file_name
                try:
                    with open(local_file_path, 'wb') as local_file:
                        ftp.retrbinary(f'RETR {file_name}', local_file.write)
                    logger.info("Downloaded file: %s", local_file_path)
                except Exception as e:
                    logger.error("Failed to download file %s: %s", file_name, e)
                    if local_file_path.exists():
                        local_file_path.unlink()
                    raise Exception(_("Failed to download file %s: %s", file_name, e))
                try:
                    ftp.delete(file_name)
                    logger.info("Deleted remote file: %s", file_name)
                except Exception as e:
                    logger.error("Failed to delete remote file %s: %s", file_name, e)
                    raise Exception(_("Failed to delete remote file %s: %s", file_name, e))
        except Exception as e:
            logger.error("Error processing FTP files: %s", e)
            raise Exception(_("Error processing FTP files: %s", e))
        finally:
            ftp.quit()

    def _process_xml_file(self, file, processed_path, record):
        logger = logging.getLogger(__name__)
        logger.info("Processing file: %s", file.name)

        tree = ET.parse(file)
        root = tree.getroot()
        nsmap = root.nsmap

        product_name = self.get_statvalue_by_id('102', root=root, nsmap=nsmap)
        product_code = self.get_statvalue_by_id('103', root=root, nsmap=nsmap)
        machine_text = self.get_text_from('Machine_Number', root=root, nsmap=nsmap)
        start_str = self.get_text_from('Production_Start', root=root, nsmap=nsmap)
        end_str = self.get_text_from('Production_End', root=root, nsmap=nsmap)
        period_str = self.get_statvalue_by_id('11', root=root, nsmap=nsmap)
        weight_nom = self.get_statvalue_by_id('21', root=root, nsmap=nsmap)
        weight_dec = self.get_statvalue_by_id('1261', root=root, nsmap=nsmap)
        unit_ok = self.get_statvalue_by_id('35', unit='6', root=root, nsmap=nsmap)
        weight_ok_tot_qty = self.get_statvalue_by_id('30', unit='4', root=root, nsmap=nsmap)
        unit_reject_low = self.get_statvalue_by_id('32', unit='6', root=root, nsmap=nsmap)
        unit_reject_exceed = self.get_statvalue_by_id('38', unit='6', root=root, nsmap=nsmap)
        if unit_ok == '0' and (unit_reject_exceed == '0' and unit_reject_low == '0'):
            logger.warning("File %s was empty.", file.name)
        else:
            fmt = "%Y-%m-%d %H:%M"
            tz = pytz.timezone(record.mdc_timezone)
            start_dt = tz.localize(datetime.strptime(start_str, fmt)).astimezone(pytz.UTC).replace(tzinfo=None) if start_str else None
            end_dt   = tz.localize(datetime.strptime(end_str, fmt)).astimezone(pytz.UTC).replace(tzinfo=None) if end_str else None
            t= datetime.strptime(period_str, "%H:%M:%S")
            period_min = t.hour * 60 + t.minute + t.second / 60
            machine_number = re.match(r'\d+', machine_text).group() if machine_text else None
            equipment = self.env['maintenance.equipment'].search([('serial_no', '=', machine_number)], limit=1)
            if not equipment or equipment.id != record.id:
                raise Exception(_(
                    "Equipment mismatch or not found.\nExpected: %(expected)s\nFound: %(found)s",
                    expected=record.name,
                    found=equipment.name if equipment else "None"
                ))
            product = self.env['product.product'].search([('default_code', '=', product_code)], limit=1)
            if not product:
                categ = (
                    record.company_id.product_categ_default_id
                    or self.env.ref("product.product_category_all", raise_if_not_found=False)
                    or self.env['product.category'].search(
                        [('company_id', '=', record.company_id.id)] if record.company_id else [('company_id', '=', False)],
                        limit=1
                    )
                )
                product_template = self.env['product.template'].sudo().create({
                    'name': product_name,
                    'default_code': product_code,
                    'detailed_type': 'consu',
                    'categ_id': categ.id,
                    'company_id': record.company_id.id or False,
                })
                product = product_template.product_variant_id
                logger.warning(
                    "Product with code %s not found. Automatically created with name '%s'.",
                    product_code,product_name
                )
                product.message_post(
                    body=_("Automatically created from file '%(file)s'",file=file.name),
                    subtype_id=self.env.ref("mail.mt_comment").id
                )

            msg = self.env['mdc.weight.record']._check_overlap_manual(equipment, start_dt, end_dt)
            if msg:
                raise Exception(msg)

            self.env['mdc.weight.record'].with_context(mdc_cron_create=True).create({
                'product_id': product.id,
                'equipment_id': equipment.id,
                'start': start_dt,
                'end': end_dt,
                'period_min': period_min,
                'weight_nom_qty': float(weight_nom or 0),
                'weight_dec_qty': float(weight_dec or 0),
                'unit_ok': int(unit_ok or 0),
                'weight_ok_tot_qty': float(weight_ok_tot_qty or 0),
                'unit_reject_low': int(unit_reject_low or 0),
                'unit_reject_exceed': int(unit_reject_exceed or 0),
            })
        processed_file = processed_path / file.name
        file.rename(processed_file)
        logger.info("Moved processed file to: %s", processed_file)
