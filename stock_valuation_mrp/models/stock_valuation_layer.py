# © 2022 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (https://www.gnu.org/licenses/lgpl-3.0.html)

from odoo import fields, models, api


class StockValuationLayer(models.Model):
    _inherit = "stock.valuation.layer"

    @api.model
    def create(self, vals):
        PHAP_sudo = self.env["product.history.average.price"].sudo()
        if vals.get("stock_move_id"):
            move_id = self.env["stock.move"].browse(vals["stock_move_id"])
            product_id = self.env['product.product'].browse(vals.get("product_id"))

            # if (not move_id.picking_id or move_id.unbuild_id or move_id.picking_code == 'mrp_operation') and product_id.categ_id.warehouse_valuation:
            if (
                move_id.unbuild_id
                or move_id.raw_material_production_id
                or move_id.production_id
            ) and product_id.categ_id.warehouse_valuation:
                # vals["create_date_valuation"] = fields.Datetime.now() # Unnecessary, better default value

                vals["accumulated"] = False
                # TODO true for an unbuild, but for a production??
                vals["document_origin"] = move_id.reference

                # if not move_id.picking_id and move_id.unbuild_id:
                # FIXME maybe better based SLV quantity sign
                # if move_id.location_id.get_warehouse():
                #     vals["warehouse_id"] = move_id.location_id.get_warehouse().id
                # else:
                #     vals["warehouse_id"] = move_id.location_dest_id.get_warehouse().id
                # Other option:
                # * move_id._is_in() => move_id.location_dest_id
                # * not move_id._is_in() => move_id.location_id
                if vals.get("quantity") > 0:
                    vals["warehouse_id"] = move_id.location_dest_id.get_warehouse().id
                else:
                    vals["warehouse_id"] = move_id.location_id.get_warehouse().id

                # Actual Date determination
                # For now, to possible sources
                # * A module that injects the related context value (for unbuilds, mrp_unbuild_advanced)
                # TODO for productions
                date = self.env.context.get(
                    "stock_move_custom_date",
                    False
                ) or fields.Datetime.now()
                # date = move_id.picking_id.scheduled_date
                # if not move_id.picking_id:
                #     date = fields.Datetime.now()

                quantity = move_id.quantity_done
                history_last_day, history_today = self.get_history_values(vals.get("product_id"), vals.get("warehouse_id"), date)

                average_price_last = history_last_day.average_price
                if history_today:
                    average_price_last = history_today.average_price

                # MRP Production
                if move_id.raw_material_production_id or move_id.production_id:
                    # Destination product, we'll recompute average-based price
                    # TODO original price calculations is more complex than
                    #      this, maybe we should take a look at it
                    # FIXME how to make later recalculations when components PHAP is changed?
                    if move_id.production_id:
                        # total_amount = 0
                        # total_qtys = 0
                        # raw_ids = move_id.production_id.move_raw_ids
                        # for component in raw_ids:
                        #     total_amount += PHAP_sudo.get_price(
                        #         component.product_id,
                        #         move_id.location_id.get_warehouse(),
                        #         dt=date
                        #     ) * component.quantity_done
                        #     total_qtys += component.quantity_done
                        # # price_unit = 0
                        # # for record in move_id.production_id.move_raw_ids:
                        # #     price_unit += record.product_id.standard_price_warehouse_ids.filtered(lambda x: x.warehouse_id.id == move_id.picking_type_id.warehouse_id.id).average_price
                        # # vals["unit_cost"] = price_unit / len(move_id.production_id.move_raw_ids)
                        # # TODO divide by zero, is it possible?
                        # vals["unit_cost"] = total_amount / total_qtys
                        vals["unit_cost"] = move_id._compute_production_svl_price(date)
                        vals["value"] = vals.get("unit_cost") * vals.get("quantity")
                        vals["accumulated"] = True
                    # Production components
                    else:
                        # vals["unit_cost"] = move_id.product_id.standard_price_warehouse_ids.filtered(lambda x: x.warehouse_id.id == move_id.picking_type_id.warehouse_id.id).average_price
                        vals["unit_cost"] = PHAP_sudo.get_price(
                            move_id.product_id,
                            move_id.location_id.get_warehouse(),
                            dt=date
                        )
                        vals["value"] = vals.get("unit_cost") * vals.get("quantity")

                # Unbuild
                elif not move_id.picking_id and move_id.unbuild_id:
                    # FIXME simplest way to obtain reference product
                    # unbuild_product = move_id.unbuild_id.produce_line_ids.filtered(lambda x: x.warehouse_id.id is False).product_id
                    unbuild_product = move_id.unbuild_id.product_id

                    # vals["unit_cost"] = unbuild_product.standard_price_warehouse_ids.filtered(lambda x: x.warehouse_id.id == vals.get("warehouse_id")).average_price
                    vals["unit_cost"] = PHAP_sudo.get_price(
                        unbuild_product,
                        move_id.unbuild_id.location_id.get_warehouse(),
                        dt=date
                    )
                    vals["value"] = vals.get("unit_cost") * vals.get("quantity")

                    # unbuild_move = move_id.unbuild_id.produce_line_ids.filtered(lambda x: x.warehouse_id.id is False)
                    # if move_id != unbuild_move:
                    #     vals["accumulated"] = True
                    vals["accumulated"] = (unbuild_product != move_id.product_id)

                if vals.get("accumulated"):
                    vals["average_price"] = (history_last_day.total_quantity * history_last_day.average_price + (history_today.summary_entry + vals.get("value"))) / (history_last_day.total_quantity + history_today.total_quantity_day + quantity)
                else:
                    if average_price_last > 0:
                        vals["average_price"] = average_price_last
                    else:
                        vals["average_price"] = history_last_day.average_price

                vals["history_average_price_id"] = self.product_history_link(vals.get("product_id"), vals.get("warehouse_id"), vals.get("average_price"), vals.get("quantity"), vals.get("value"), vals.get("accumulated"), history_today, date)

        return super(StockValuationLayer, self).create(vals)
