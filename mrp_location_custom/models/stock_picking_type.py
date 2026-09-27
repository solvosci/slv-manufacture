from odoo import api, fields, models


class StockPickingType(models.Model):
    _inherit = 'stock.picking.type'

    is_pbm_manufacture_type = fields.Boolean(
        string='Is PBM Manufacture Type',
        compute='_compute_is_pbm_manufacture_type',
    )

    mrp_custom_src_location = fields.Boolean(
        string='Custom source location per manufacturing order',
        compute='_compute_mrp_custom_src_location',
        store=True,
        readonly=False,
        help=(
            'When enabled, each new manufacturing order created with this operation type '
            'will automatically generate a child location under the warehouse Pre-Production '
            'area, assigned as the exclusive source location for that order.\n\n'
            'Only applicable to manufacturing operation types in warehouses configured '
            'with two or three-step manufacturing (pbm / pbm_sam). '
            'Automatically disabled if the warehouse manufacturing steps change.'
        ),
    )

    @api.depends('code', 'warehouse_id', 'warehouse_id.manufacture_steps')
    def _compute_is_pbm_manufacture_type(self):
        pbm = self.filtered(
            lambda pt: pt.code == 'mrp_operation'
            and pt.warehouse_id.manufacture_steps in ('pbm', 'pbm_sam')
        )
        pbm.is_pbm_manufacture_type = True
        (self - pbm).is_pbm_manufacture_type = False

    @api.depends('is_pbm_manufacture_type')
    def _compute_mrp_custom_src_location(self):
        # When the operation type is no longer pbm-compatible, force the flag to False.
        # Records that still qualify are left untouched (their stored value is kept).
        non_pbm = self.filtered(lambda pt: not pt.is_pbm_manufacture_type)
        non_pbm.mrp_custom_src_location = False

    @api.onchange('mrp_custom_src_location')
    def _onchange_mrp_custom_src_location(self):
        if not self.mrp_custom_src_location:
            return {
                'warning': {
                    'title': 'Warning',
                    'message': (
                        'Disabling this option will not affect manufacturing orders that '
                        'have already been created. Only new orders will be impacted.'
                    ),
                }
            }
