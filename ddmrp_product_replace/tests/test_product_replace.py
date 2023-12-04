# Copyright 2018 Camptocamp SA
# Copyright 2018-21 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from datetime import datetime, timedelta

from odoo.addons.ddmrp.tests.common import TestDdmrpCommon


class TestDDMRPProductReplace(TestDdmrpCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.buffer = cls.env.ref("ddmrp.stock_buffer_rm01")
        cls.old_product = cls.env.ref("ddmrp.product_product_rm01")
        cls.put_away_rule_obj = cls.env["stock.putaway.rule"]
        cls.old_product.write(
            {
                "route_ids": [
                    (6, 0, [cls.env.ref("mrp.route_warehouse0_manufacture").id])
                ],
            }
        )
        cls.old_product_putaway = cls.put_away_rule_obj.create(
            {
                "product_id": cls.old_product.id,
                "location_in_id": cls.env.ref("stock.stock_location_stock").id,
                "location_out_id": cls.env.ref("stock.stock_location_components").id,
            }
        )
        # Change adu method:
        method = cls.env.ref("ddmrp.adu_calculation_method_past_120")
        cls.buffer.adu_calculation_method = method

    def test_01_product_replace_use_existing(self):
        date_move = datetime.today() - timedelta(days=30)
        picking = self.create_picking_out(self.old_product, date_move, 60)
        self._do_picking(picking, date_move)
        self.buffer._calc_adu()
        adu_previous = 60 / 120
        self.assertEqual(self.buffer.adu, adu_previous)
        self.assertEqual(self.buffer.product_id, self.old_product)
        self.assertEqual(len(self.buffer.demand_product_ids), 0)

        wiz = self.env["ddmrp.product.replace"].create(
            {
                "mode": "use_existing",
                "old_product_ids": [(6, 0, self.buffer.product_id.ids)],
                "use_existing": "new",
                "new_product_name": "RM-01 Replacement",
                "new_product_default_code": "ABCDE012345",
                "copy_route": True,
                "copy_putaway": True,
            }
        )
        self.assertEqual(wiz.buffer_ids, self.buffer)
        new_product_id = wiz.button_validate().get("res_id")
        new_product = self.env["product.product"].browse(new_product_id)

        self.assertEqual(new_product.name, "RM-01 Replacement")
        self.assertEqual(new_product.default_code, "ABCDE012345")
        self.assertEqual(new_product.route_ids, self.old_product.route_ids)

        new_product_putaway = self.put_away_rule_obj.search(
            [("product_id", "=", new_product.id)]
        )
        new_putaway_tuple = (
            new_product_putaway.location_in_id.id,
            new_product_putaway.location_out_id.id,
        )
        for putaway in self.old_product_putaway:
            putaway_tuple = (putaway.location_in_id.id, putaway.location_out_id.id)
            self.assertEqual(putaway_tuple, new_putaway_tuple)

        self.assertEqual(self.buffer.product_id, new_product)
        self.assertIn(self.old_product, self.buffer.demand_product_ids)
        self.buffer._calc_adu()
        self.assertEqual(self.buffer.adu, adu_previous)

    def test_02_product_replace_new_buffer(self):
        # Complete one delivery
        date_move = datetime.today() - timedelta(days=30)
        picking = self.create_picking_out(self.old_product, date_move, 60)
        self._do_picking(picking, date_move)
        # and confirm an incoming
        self.create_picking_in(self.old_product, datetime.today(), 30)
        self.buffer.cron_actions()
        self.assertEqual(self.buffer.product_id, self.old_product)
        self.assertEqual(len(self.buffer.demand_product_ids), 0)
        old_onhand = self.buffer.product_location_qty_available_not_res
        self.assertEqual(old_onhand, -60.0)
        old_incoming_dlt_qty = self.buffer.incoming_dlt_qty
        self.assertEqual(old_incoming_dlt_qty, 30.0)
        old_incoming_qty = self.buffer.incoming_total_qty
        self.assertEqual(old_incoming_qty, 30.0)
        wiz = self.env["ddmrp.product.replace"].create(
            {
                "mode": "new_buffer",
                "old_product_ids": [(6, 0, self.buffer.product_id.ids)],
                "use_existing": "new",
                "new_product_name": "RM-01 Replacement 2",
                "new_product_default_code": "ABC000222",
                "copy_route": True,
                "copy_putaway": False,
            }
        )
        self.assertEqual(wiz.buffer_ids, self.buffer)
        self.assertFalse(wiz.is_already_replaced)
        res = wiz.button_validate()
        new_buffer_ids = res.get("domain")[0][2]
        model = res.get("res_model")
        self.assertEqual(model, "stock.buffer")
        new_buffer = self.bufferModel.browse(new_buffer_ids)
        self.assertEqual(len(new_buffer), 1)
        self.assertNotEqual(self.buffer.id, new_buffer.id)
        # Check new product
        new_product = new_buffer.product_id
        self.assertEqual(new_product.name, "RM-01 Replacement 2")
        self.assertEqual(new_product.default_code, "ABC000222")
        self.assertEqual(new_product.route_ids, self.old_product.route_ids)
        self.assertNotEqual(self.buffer.product_id, new_product)
        # Check replacing fields in buffers:
        self.assertEqual(self.buffer.replaced_by_id, new_buffer)
        self.assertTrue(new_buffer.is_replacement_product)
        self.assertTrue(new_buffer.use_replacement_for_buffer_status)
        # Check buffer values:
        self.buffer.cron_actions()
        self.assertEqual(old_onhand, new_buffer.product_location_qty_available_not_res)
        self.assertEqual(old_incoming_dlt_qty, new_buffer.incoming_dlt_qty)
        self.assertEqual(old_incoming_qty, new_buffer.incoming_total_qty)
        new_buffer.invalidate_recordset()
        new_buffer.use_replacement_for_buffer_status = False
        new_buffer.cron_actions()
        self.assertNotEqual(
            old_onhand, new_buffer.product_location_qty_available_not_res
        )
        self.assertNotEqual(old_incoming_dlt_qty, new_buffer.incoming_dlt_qty)
        self.assertNotEqual(old_incoming_qty, new_buffer.incoming_total_qty)
        # Demand:
        self.assertIn(self.old_product, new_buffer.demand_product_ids)
        self.assertEqual(new_buffer.qualified_demand, 0)
        self.create_picking_out(self.old_product, datetime.today(), 11)
        self.buffer.cron_actions()
        self.assertEqual(self.buffer.qualified_demand, 11)
        new_buffer.cron_actions()
        self.assertEqual(new_buffer.qualified_demand, 11)
