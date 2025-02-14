# © 2025 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3 - See https://www.gnu.org/licenses/lgpl-3.0.html

from odoo import fields, models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    product_document_urls = fields.Text(
        string=" Product Documents",
        compute="_compute_get_product_document_urls"
    )

    def _compute_get_product_document_urls(self):
        for production in self:
            prod_attachments = self.env["ir.attachment"].search(
                [                
                    ("res_model", "=", "product.product"),
                    ("res_id", "=", production.product_id.id),
                ]
            )
            tmpl_attachments = self.env["ir.attachment"].search(
                [                
                    ("res_model", "=", "product.template"),
                    ("res_id", "=", production.product_id.product_tmpl_id.id),
                ]
            )
            attachments = (prod_attachments | tmpl_attachments)
            document_list=[]
            for document in attachments:
                if document.type == "url" and document.url:
                    document_list.append(f'<a href="{document.url}" target="_blank">{document.name}</a>')
                else:
                    file_url = f"/web/content/{document.id}"
                    document_list.append(f'<a href="{file_url}" target="_blank">{document.name}</a>')

            production.product_document_urls = "<br/>".join(document_list)
