# © 2025 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (https://www.gnu.org/licenses/lgpl-3.0.html)

from odoo import _, models
from odoo.exceptions import ValidationError


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    def action_back_to_draft(self):
        self.ensure_one()
        if self.state != "done":
            raise ValidationError(_("Only done production can be backed to draft"))
        old_state = self.state
        bypass_permissions = self.env.context.get(
            "mrp_production_undo_bypass_permissions", False
        )
        if not (
            bypass_permissions or self.env.user.has_group(
                "mrp_production_undo.group_mrp_production_undo"
            )
        ):
            raise ValidationError(
                _("You don't have permissions to back production to draft")
            )
        
        # ---------------------------------------------------------------------
        # TODO
        # (1) Obtain both consumed and produced move lines
        consume_move_ids = self.move_raw_ids.filtered(
            lambda x: x.state == "done"
        )
        finished_move_ids = self.move_finished_ids.filtered(
            lambda x: x.state == "done"
        )
        mrp_move_ids = (consume_move_ids + finished_move_ids)
        # (2) Call hook for safe removal for them
        mrp_move_ids._mrp_check_safe_removal()
        # (3) For every done move line, update Quant entry
        Quant = self.env["stock.quant"]
        mls = mrp_move_ids.move_line_ids
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
        # (4) Set produced and consumed moves to draft
        mrp_move_ids.write({"state": "draft"})
        # (5) For boths set of moves, call unlink_previous_stuff hook...
        mrp_move_ids._mrp_unlink_previous_stuff()
        # (6) ... but only remove produced moves and consumed move lines, not moves
        finished_move_ids.unlink()
        consume_move_ids.move_line_ids.unlink()
        # (7) Set back to draft state whole production
        self.write({"state": "draft"})
        # ---------------------------------------------------------------------

        message = _(
            "Production has been backed to draft from ""%s"" state."
        ) % old_state
        if bypass_permissions:
            message = "%s\n\n%s" % (message, _("Operation's been done bypassing permissions."))
        self.message_post(body=message)
