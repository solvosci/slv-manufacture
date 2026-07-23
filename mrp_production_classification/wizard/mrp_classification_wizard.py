# Copyright 2026 Solvos Consultoría Informática, S.L. (<https://www.solvos.es>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare, float_is_zero


class MrpClassificationWizard(models.TransientModel):
    _name = "mrp.classification.wizard"
    _description = "Classification Distribution Wizard"

    production_id = fields.Many2one("mrp.production", required=True, readonly=True)
    raw_move_id = fields.Many2one(
        "stock.move",
        required=True,
        readonly=True,
        help="Move of the bulk component being consumed.",
    )
    original_product_id = fields.Many2one(
        related="raw_move_id.product_id", string="Original Product"
    )
    product_uom_id = fields.Many2one(
        related="raw_move_id.product_uom", string="Unit of Measure"
    )

    qty_to_consume = fields.Float(
        string="Planned Quantity (Initial Demand)",
        digits="Product Unit",
        readonly=True,
    )

    line_ids = fields.One2many(
        "mrp.classification.wizard.line", "wizard_id", string="Classification Result"
    )

    total_distributed = fields.Float(
        string="Total Distributed",
        compute="_compute_totals",
        digits="Product Unit",
    )
    difference = fields.Float(
        string="Consumed - Planned", compute="_compute_totals", digits="Product Unit"
    )
    force_confirm = fields.Boolean(
        string="Confirm even if it differs from the plan",
        help="Check this box to confirm the classification even if the "
        "total distributed does not match the initially planned quantity.",
    )

    confirm_and_process = fields.Boolean(
        string="Complete Manufacturing Order",
        default=True,
        help="If checked, the manufacturing order is marked as done "
        "immediately after confirming the classification.",
    )

    @api.depends("line_ids.qty", "line_ids.product_uom_id", "qty_to_consume")
    def _compute_totals(self):
        for record in self:
            raw_uom = record.raw_move_id.product_uom
            total = 0.0
            for line in record.line_ids:
                total += line.product_uom_id._compute_quantity(
                    line.qty, raw_uom, round=False
                )
            record.total_distributed = total
            record.difference = record.total_distributed - record.qty_to_consume

    def _prepare_lines(self):
        self.ensure_one()
        production = self.production_id
        moves = production.move_finished_ids.filtered(lambda m: m.state != "cancel")
        serial_tracked = moves.product_id.filtered(lambda p: p.tracking == "serial")
        if serial_tracked:
            raise UserError(
                self.env._(
                    "This wizard does not support products tracked by unique "
                    "Serial Number. Configure these products with Lot tracking."
                )
            )

        raw_uom = self.raw_move_id.product_uom
        uom_error = moves.filtered(
            lambda m: not m.product_uom._has_common_reference(raw_uom)
        )
        if uom_error:
            raise UserError(
                self.env._(
                    "The unit of measure of these products is not compatible "
                    "with that of the bulk component."
                )
            )

        vals_list = []
        for move in moves:
            if move.product_id == production.product_id:
                existing_lot = production.lot_producing_ids[:1]
            else:
                existing_lot = move.move_line_ids.lot_id[:1]
            vals_list.append(
                {
                    "wizard_id": self.id,
                    "move_id": move.id,
                    "product_id": move.product_id.id,
                    "product_uom_id": move.product_uom.id,
                    "qty": move.product_uom_qty,
                    "lot_id": existing_lot.id,
                    "lot_name": False,
                }
            )
        self.env["mrp.classification.wizard.line"].create(vals_list)

    def button_confirm(self):
        self.ensure_one()
        precision = self.env["decimal.precision"].precision_get("Product Unit")

        if (
            float_compare(
                self.total_distributed, self.qty_to_consume, precision_digits=precision
            )
            != 0
            and not self.force_confirm
        ):
            raise UserError(
                self.env._(
                    "The total distributed (%(total)s) differs "
                    "from the initially planned quantity (%(planned)s).",
                    total=self.total_distributed,
                    planned=self.qty_to_consume,
                )
            )

        for line in self.line_ids.filtered(
            lambda x: float_compare(x.qty, 0.0, precision_digits=precision) < 0
        ):
            raise UserError(
                self.env._(
                    "The quantity of %s cannot be negative.",
                    line.product_id.display_name,
                )
            )

        production = self.production_id
        main_line = self.line_ids.filtered(
            lambda x: x.move_id.product_id == production.product_id
        )
        if len(main_line) != 1:
            raise UserError(
                self.env._(
                    "Cannot find the main product line "
                    "(%s) in the distribution.",
                    production.product_id.display_name,
                )
            )

        if float_is_zero(main_line.qty, precision_digits=precision):
            raise UserError(
                self.env._(
                    "The order's main product cannot end up at 0 after the distribution."
                )
            )

        byproduct_lines = self.line_ids - main_line

        # do_not_unreserve: without it, writing product_uom_qty on a move fed
        # by an upstream transfer (2/3-step manufacturing routes) makes Odoo
        # fully release its reservation instead of shrinking it gracefully;
        # we adjust it ourselves right after, in _consume_raw_material().
        self.raw_move_id.with_context(do_not_unreserve=True).write(
            {"product_uom_qty": self.total_distributed}
        )
        self._consume_raw_material()

        main_qty = main_line.product_uom_id._compute_quantity(
            main_line.qty, production.product_uom_id
        )
        production.qty_producing = main_qty
        production.product_qty = main_qty
        main_line.move_id.product_uom_qty = main_qty
        if production.product_id.tracking != "none":
            production.lot_producing_ids = main_line._get_or_create_lot()

        for line in byproduct_lines:
            if float_is_zero(line.qty, precision_digits=precision):
                line.move_id.product_uom_qty = 0.0
                self._write_move_quantity(line.move_id, 0.0, lot=False)
                continue
            lot = (
                line._get_or_create_lot()
                if line.product_id.tracking != "none"
                else False
            )
            line.move_id.product_uom_qty = line.qty
            self._write_move_quantity(line.move_id, line.qty, lot=lot)

        if not self.confirm_and_process:
            return False

        return production.button_mark_done()

    def _consume_raw_material(self):
        self.ensure_one()
        move = self.raw_move_id
        move.manual_consumption = True
        lines = move.move_line_ids

        if not lines:
            if move.product_id.tracking != "none":
                raise UserError(
                    self.env._(
                        "There is no stock reserved for this order, so the "
                        "source lot cannot be determined."
                    )
                )
            self._write_move_quantity(move, self.total_distributed, lot=False)
            return

        precision = self.env["decimal.precision"].precision_get("Product Unit")
        reserved_total = sum(lines.mapped("quantity"))
        delta = self.total_distributed - reserved_total

        if float_is_zero(delta, precision_digits=precision):
            lines.write({"picked": True})
            return

        if delta > 0:
            move.product_uom_qty = self.total_distributed
            move._action_assign(force_qty=delta)
            lines = move.move_line_ids
            new_total = sum(lines.mapped("quantity"))
            if (
                float_compare(
                    new_total, self.total_distributed, precision_digits=precision
                )
                < 0
            ):
                raise UserError(
                    self.env._(
                        "There is not enough stock in the warehouse to cover "
                        "the total distributed. Check availability before "
                        "classifying."
                    )
                )
            lines.write({"picked": True})
            return

        for current_line in reversed(lines):
            if float_is_zero(delta, precision_digits=precision):
                break
            shrink = move.product_uom.round(min(-delta, current_line.quantity))
            current_line.quantity = current_line.quantity - shrink
            delta += shrink

        lines.write({"picked": True})

    def _write_move_quantity(self, move, qty, lot=False):
        lines = move.move_line_ids
        vals = {
            "quantity": qty,
            "picked": True,
            "lot_id": lot.id if lot else False,
        }
        if lines:
            lines[0].write(vals)
            stale = lines[1:]
            if stale:
                stale.unlink()
        else:
            vals.update(
                {
                    "move_id": move.id,
                    "product_id": move.product_id.id,
                    "product_uom_id": move.product_uom.id,
                    "location_id": move.location_id.id,
                    "location_dest_id": move.location_dest_id.id,
                    "company_id": move.company_id.id,
                }
            )
            self.env["stock.move.line"].create(vals)
