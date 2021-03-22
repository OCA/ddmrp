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

    def test_product_replace(self):
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
                "old_product_id": self.buffer.product_id.id,
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
