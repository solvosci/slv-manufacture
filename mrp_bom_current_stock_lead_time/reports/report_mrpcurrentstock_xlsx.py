# © 2026 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3.0 - See (https://www.gnu.org/licenses/agpl-3.0).

import logging

from odoo import models
from odoo.tools.translate import _

_logger = logging.getLogger(__name__)


class ReportMrpBomCurrentStockXlsx(models.AbstractModel):
    _inherit = "report.mrp_bom_current_stock.report_mrpbom_current_stock_xlsx"
    _inherit = "report.report_xlsx.abstract"


# To Do
# Add lead time information to the report.
# The lead time of the BoM is calculated based on the lead time of the components
# and the lead time of the BoM itself. The maximum lead time of the components is used to calculate the lead time of the BoM.
