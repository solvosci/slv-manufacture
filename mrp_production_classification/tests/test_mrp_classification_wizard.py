# Copyright 2026 Solvos Consultoría Informática, S.L. (<https://www.solvos.es>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo.exceptions import UserError
from odoo.tests.common import tagged

from odoo.addons.base.tests.common import BaseCommon


@tagged("post_install", "-at_install")
class TestMrpClassificationWizard(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.uom_kg = cls.env.ref("uom.product_uom_kgm")
        cls.uom_unit = cls.env.ref("uom.product_uom_unit")

        cls.warehouse = cls.env["stock.warehouse"].search(
            [("company_id", "=", cls.env.company.id)], limit=1
        )
        cls.location = cls.warehouse.lot_stock_id
        cls.picking_type = cls.env["stock.picking.type"].create(
            {
                "name": "Test Classification",
                "code": "mrp_operation",
                "sequence_code": "TSTCLS",
                "warehouse_id": cls.warehouse.id,
                "is_classification": True,
            }
        )

        cls.bulk_product = cls.env["product.product"].create(
            {
                "name": "Bulk",
                "type": "consu",
                "is_storable": True,
                "tracking": "lot",
                "uom_id": cls.uom_kg.id,
            }
        )
        cls.main_product = cls.env["product.product"].create(
            {
                "name": "Main",
                "type": "consu",
                "is_storable": True,
                "tracking": "lot",
                "uom_id": cls.uom_kg.id,
            }
        )
        cls.byproduct = cls.env["product.product"].create(
            {
                "name": "Byproduct",
                "type": "consu",
                "is_storable": True,
                "tracking": "lot",
                "uom_id": cls.uom_kg.id,
            }
        )

        cls.bom = cls.env["mrp.bom"].create(
            {
                "product_id": cls.main_product.id,
                "product_tmpl_id": cls.main_product.product_tmpl_id.id,
                "product_qty": 1.0,
                "product_uom_id": cls.uom_kg.id,
                "type": "normal",
                "consumption": "flexible",
                "bom_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": cls.bulk_product.id,
                            "product_qty": 1.0,
                            "product_uom_id": cls.uom_kg.id,
                        },
                    )
                ],
                "byproduct_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": cls.byproduct.id,
                            "product_qty": 0.5,
                            "product_uom_id": cls.uom_kg.id,
                        },
                    )
                ],
            }
        )

    def _make_lot(self, product, name, qty):
        lot = self.env["stock.lot"].create(
            {
                "product_id": product.id,
                "name": name,
                "company_id": self.env.company.id,
            }
        )
        if qty:
            self.env["stock.quant"]._update_available_quantity(
                product, self.location, qty, lot_id=lot
            )
        return lot

    def _create_production(self, qty=100.0, bom=None):
        production = self.env["mrp.production"].create(
            {
                "product_id": self.main_product.id,
                "product_qty": qty,
                "product_uom_id": self.uom_kg.id,
                "bom_id": (bom or self.bom).id,
                "picking_type_id": self.picking_type.id,
                "company_id": self.env.company.id,
            }
        )
        production.action_confirm()
        production.action_assign()
        return production

    def _open_wizard(self, production, confirm_and_process=False):
        wizard_id = production.action_open_classification_wizard()["res_id"]
        wizard = self.env["mrp.classification.wizard"].browse(wizard_id)
        wizard.confirm_and_process = confirm_and_process
        return wizard

    def _main_and_byproduct_lines(self, wizard):
        main_line = wizard.line_ids.filtered(
            lambda x: x.product_id == self.main_product
        )
        byproduct_line = wizard.line_ids - main_line
        return main_line, byproduct_line

    def test_requires_single_bulk_component(self):
        second_bulk = self.env["product.product"].create(
            {
                "name": "Second Bulk",
                "type": "consu",
                "is_storable": True,
                "tracking": "lot",
                "uom_id": self.uom_kg.id,
            }
        )
        bom = self.env["mrp.bom"].create(
            {
                "product_id": self.main_product.id,
                "product_tmpl_id": self.main_product.product_tmpl_id.id,
                "product_qty": 1.0,
                "product_uom_id": self.uom_kg.id,
                "type": "normal",
                "consumption": "flexible",
                "bom_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.bulk_product.id,
                            "product_qty": 1.0,
                            "product_uom_id": self.uom_kg.id,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "product_id": second_bulk.id,
                            "product_qty": 1.0,
                            "product_uom_id": self.uom_kg.id,
                        },
                    ),
                ],
            }
        )
        self._make_lot(self.bulk_product, "BULK-0", 100.0)
        self._make_lot(second_bulk, "BULK-0-B", 100.0)
        production = self._create_production(bom=bom)
        with self.assertRaises(UserError):
            production.action_open_classification_wizard()

    def test_prepare_lines_rejects_serial_tracking(self):
        serial_byproduct = self.env["product.product"].create(
            {
                "name": "Serial Byproduct",
                "type": "consu",
                "is_storable": True,
                "tracking": "serial",
                "uom_id": self.uom_kg.id,
            }
        )
        bom = self.env["mrp.bom"].create(
            {
                "product_id": self.main_product.id,
                "product_tmpl_id": self.main_product.product_tmpl_id.id,
                "product_qty": 1.0,
                "product_uom_id": self.uom_kg.id,
                "type": "normal",
                "consumption": "flexible",
                "bom_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.bulk_product.id,
                            "product_qty": 1.0,
                            "product_uom_id": self.uom_kg.id,
                        },
                    )
                ],
                "byproduct_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": serial_byproduct.id,
                            "product_qty": 0.5,
                            "product_uom_id": self.uom_kg.id,
                        },
                    )
                ],
            }
        )
        self._make_lot(self.bulk_product, "BULK-2", 100.0)
        production = self._create_production(bom=bom)
        with self.assertRaises(UserError):
            production.action_open_classification_wizard()

    def test_prepare_lines_rejects_incompatible_uom(self):
        incompatible_byproduct = self.env["product.product"].create(
            {
                "name": "Incompatible UoM Byproduct",
                "type": "consu",
                "is_storable": True,
                "uom_id": self.uom_unit.id,
            }
        )
        bom = self.env["mrp.bom"].create(
            {
                "product_id": self.main_product.id,
                "product_tmpl_id": self.main_product.product_tmpl_id.id,
                "product_qty": 1.0,
                "product_uom_id": self.uom_kg.id,
                "type": "normal",
                "consumption": "flexible",
                "bom_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.bulk_product.id,
                            "product_qty": 1.0,
                            "product_uom_id": self.uom_kg.id,
                        },
                    )
                ],
                "byproduct_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": incompatible_byproduct.id,
                            "product_qty": 1.0,
                            "product_uom_id": self.uom_unit.id,
                        },
                    )
                ],
            }
        )
        self._make_lot(self.bulk_product, "BULK-3", 100.0)
        production = self._create_production(bom=bom)
        with self.assertRaises(UserError):
            production.action_open_classification_wizard()

    def test_total_mismatch_requires_force_confirm(self):
        self._make_lot(self.bulk_product, "BULK-4", 100.0)
        production = self._create_production()
        wizard = self._open_wizard(production)
        main_line, byproduct_line = self._main_and_byproduct_lines(wizard)
        main_line.qty = 50.0
        main_line.lot_name = "MAIN-MISMATCH"
        byproduct_line.qty = 10.0
        byproduct_line.lot_name = "BY-MISMATCH"

        with self.assertRaises(UserError):
            wizard.button_confirm()

        wizard.force_confirm = True
        wizard.button_confirm()

    def test_main_product_cannot_end_at_zero(self):
        self._make_lot(self.bulk_product, "BULK-5", 100.0)
        production = self._create_production()
        wizard = self._open_wizard(production)
        main_line, byproduct_line = self._main_and_byproduct_lines(wizard)
        main_line.qty = 0.0
        byproduct_line.qty = 100.0
        wizard.force_confirm = True
        with self.assertRaises(UserError):
            wizard.button_confirm()

    def test_negative_quantity_raises(self):
        self._make_lot(self.bulk_product, "BULK-6", 100.0)
        production = self._create_production()
        wizard = self._open_wizard(production)
        main_line, __ = self._main_and_byproduct_lines(wizard)
        main_line.qty = -10.0
        wizard.force_confirm = True
        with self.assertRaises(UserError):
            wizard.button_confirm()

    def test_classify_distributes_main_and_byproduct(self):
        self._make_lot(self.bulk_product, "BULK-7", 100.0)
        production = self._create_production()
        wizard = self._open_wizard(production)
        main_line, byproduct_line = self._main_and_byproduct_lines(wizard)
        main_line.qty = 70.0
        main_line.lot_name = "MAIN-LOT-1"
        byproduct_line.qty = 30.0
        byproduct_line.lot_name = "BY-LOT-1"

        wizard.button_confirm()

        self.assertEqual(production.qty_producing, 70.0)
        self.assertEqual(production.lot_producing_ids.name, "MAIN-LOT-1")
        byproduct_move = production.move_finished_ids.filtered(
            lambda m: m.product_id == self.byproduct
        )
        self.assertEqual(byproduct_move.product_uom_qty, 30.0)
        self.assertEqual(byproduct_move.move_line_ids.lot_id.name, "BY-LOT-1")

    def test_get_or_create_lot_reuses_existing_lot(self):
        existing = self._make_lot(self.byproduct, "EXISTING-LOT", 0.0)
        self._make_lot(self.bulk_product, "BULK-8", 100.0)
        production = self._create_production()
        wizard = self._open_wizard(production)
        main_line, byproduct_line = self._main_and_byproduct_lines(wizard)
        main_line.qty = 70.0
        main_line.lot_name = "MAIN-REUSE"
        byproduct_line.qty = 30.0
        byproduct_line.lot_id = existing

        wizard.button_confirm()

        byproduct_move = production.move_finished_ids.filtered(
            lambda m: m.product_id == self.byproduct
        )
        self.assertEqual(byproduct_move.move_line_ids.lot_id, existing)

    def test_prepare_lines_prefills_lots_from_previous_pass(self):
        self._make_lot(self.bulk_product, "BULK-10", 100.0)
        production = self._create_production()

        wizard1 = self._open_wizard(production)
        main_line1, byproduct_line1 = self._main_and_byproduct_lines(wizard1)
        main_line1.qty = 60.0
        main_line1.lot_name = "MAIN-PREFILL"
        byproduct_line1.qty = 40.0
        byproduct_line1.lot_name = "BY-PREFILL"
        wizard1.button_confirm()

        wizard2 = self._open_wizard(production)
        main_line2, byproduct_line2 = self._main_and_byproduct_lines(wizard2)

        self.assertEqual(main_line2.lot_id.name, "MAIN-PREFILL")
        self.assertEqual(byproduct_line2.lot_id.name, "BY-PREFILL")

    def test_confirm_and_process_marks_production_done(self):
        self._make_lot(self.bulk_product, "BULK-9", 100.0)
        production = self._create_production()
        wizard = self._open_wizard(production, confirm_and_process=True)
        main_line, byproduct_line = self._main_and_byproduct_lines(wizard)
        main_line.qty = 70.0
        main_line.lot_name = "MAIN-DONE"
        byproduct_line.qty = 30.0
        byproduct_line.lot_name = "BY-DONE"

        wizard.button_confirm()

        self.assertEqual(production.state, "done")

    def test_sequential_shrink_touches_last_lot_first(self):
        self._make_lot(self.bulk_product, "LOT-A", 200.0)
        self._make_lot(self.bulk_product, "LOT-B", 200.0)
        self._make_lot(self.bulk_product, "LOT-C", 200.0)
        production = self._create_production(qty=500.0)

        reserved = {
            line.lot_id.name: line.quantity
            for line in production.move_raw_ids.move_line_ids
        }
        self.assertEqual(reserved, {"LOT-A": 200.0, "LOT-B": 200.0, "LOT-C": 100.0})

        wizard = self._open_wizard(production)
        main_line, byproduct_line = self._main_and_byproduct_lines(wizard)
        main_line.qty = 170.0
        main_line.lot_name = "MAIN-SHRINK"
        byproduct_line.qty = 80.0
        byproduct_line.lot_name = "BY-SHRINK"
        wizard.force_confirm = True
        wizard.button_confirm()
        consumed = {
            line.lot_id.name: line.quantity
            for line in production.move_raw_ids.move_line_ids
        }
        self.assertEqual(consumed["LOT-A"], 200.0)
        self.assertEqual(consumed.get("LOT-C", 0.0), 0.0)
        self.assertEqual(consumed.get("LOT-B", 0.0), 50.0)

    def test_reclassify_upward_after_shrink_does_not_block(self):
        self._make_lot(self.bulk_product, "LOT-ONLY", 100.0)
        production = self._create_production()

        wizard1 = self._open_wizard(production)
        main_line1, byproduct_line1 = self._main_and_byproduct_lines(wizard1)
        main_line1.qty = 20.0
        main_line1.lot_name = "MAIN-1"
        byproduct_line1.qty = 50.0
        byproduct_line1.lot_name = "BY-1"
        wizard1.force_confirm = True
        wizard1.button_confirm()

        wizard2 = self._open_wizard(production)
        main_line2, byproduct_line2 = self._main_and_byproduct_lines(wizard2)
        main_line2.qty = 40.0
        main_line2.lot_name = "MAIN-2"
        byproduct_line2.qty = 60.0
        byproduct_line2.lot_name = "BY-2"
        wizard2.force_confirm = True
        wizard2.button_confirm()

        raw_lines = production.move_raw_ids.move_line_ids
        self.assertEqual(len(raw_lines), 1)
        self.assertEqual(raw_lines.lot_id.name, "LOT-ONLY")
        self.assertEqual(raw_lines.quantity, 100.0)
