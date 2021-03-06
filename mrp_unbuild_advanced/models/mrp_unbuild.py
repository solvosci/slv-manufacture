# © 2021 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (https://www.gnu.org/licenses/lgpl-3.0.html)

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class MrpUnbuild(models.Model):
    _inherit = "mrp.unbuild"

    unbuild_date = fields.Datetime(
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)], 'done': [('readonly', True)]},
        default=fields.Datetime.now,
        help="This date will be used in further stock moves,"
        " when unbuild is done",
    )

    shift_start_date = fields.Datetime(
        states={"draft": [("required", False)], "done": [("required", True)]},
    )
    shift_end_date = fields.Datetime(
        states={"draft": [("required", False)], "done": [("required", True)]},
    )
    shift_total_time = fields.Float(
        states={"draft": [("required", False)], "done": [("required", True)]},
        default=8,
    )
    shift_break_time = fields.Float(
        states={"draft": [("required", False)], "done": [("required", True)]},
    )
    shift_stop_time = fields.Float()

    notes = fields.Text()

    tag_ids = fields.Many2many(
        string="Tags",
        comodel_name="mrp.tag",
    )

    @api.constrains("unbuild_date")
    def _check_unbuild_date(self):
        if self.unbuild_date > fields.Datetime.now():
            raise ValidationError(_("Unbuild date cannot be in the future!"))

    @api.constrains("shift_start_date", "shift_end_date")
    def _check_shift_dates(self):
        if self.shift_start_date and self.shift_end_date and (
            self.shift_start_date > self.shift_end_date
        ):
            raise ValidationError(_(
                "Shift end date must be older than start date!"
            ))

    def action_validate(self):
        for unbuild in self:
            if not (unbuild.shift_start_date and unbuild.shift_end_date):
                raise ValidationError(_(
                    "Shift dates must be filled before"
                    " unbuild action for %s is performed!"
                ) % unbuild.name)
        return super().action_validate()

    def action_unbuild(self):
        unbuild = self.with_context(stock_move_custom_date=self.unbuild_date)
        return super(MrpUnbuild, unbuild).action_unbuild()

    def action_back_draft(self):
        """
        Undo generated moves, updating stock inventory
        """
        self.ensure_one()
        moves = (self.consume_line_ids + self.produce_line_ids)
        moves._check_safe_removal()

        Quant = self.env["stock.quant"]
        mls = moves.move_line_ids
        for ml in mls:
            available_qty, in_date = Quant._update_available_quantity(
                ml.product_id, ml.location_id, ml.qty_done,
                lot_id=ml.lot_id, package_id=ml.package_id,
                owner_id=ml.owner_id,
            )
            Quant._update_available_quantity(
                ml.product_id, ml.location_dest_id, -ml.qty_done,
                lot_id=ml.lot_id, package_id=ml.result_package_id,
                owner_id=ml.owner_id, in_date=in_date,
            )

        moves.write({"state": "draft"})
        moves._unlink_previous_stuff()
        moves.unlink()
        self.state = "draft"
