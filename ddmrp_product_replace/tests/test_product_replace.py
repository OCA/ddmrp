# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import TransactionCase


class TestDDMRPProductReplace(TransactionCase):
    def setUp(self):
        super().setUp()
        self.orderpoint = self.env.ref("ddmrp.stock_warehouse_orderpoint_rm01")
        self.old_product = self.env.ref("ddmrp.product_product_rm01")
        self.putaway = self.env["product.putaway"].create(
            {
                "name": "Test per product",
                # 'method': 'per_product'
            }
        )
        self.old_product.write(
            {
                "route_ids": [
                    (6, 0, [self.env.ref("mrp.route_warehouse0_manufacture").id])
                ],
                "product_putaway_ids": [
                    (
                        0,
                        0,
                        {
                            "putaway_id": self.putaway.id,
                            "product_tmpl_id": self.old_product.product_tmpl_id.id,
                            "fixed_location_id": self.env.ref(
                                "stock.stock_location_components"
                            ).id,
                        },
                    )
                ],
            }
        )

    def test_product_replace(self):
        self.assertEqual(self.orderpoint.product_id, self.old_product)
        self.assertEqual(len(self.orderpoint.demand_product_ids), 0)

        wiz = self.env["ddmrp.product.replace"].create(
            {
                "old_product_id": self.orderpoint.product_id.id,
                "use_existing": "new",
                "new_product_name": "RM-01 Replacement",
                "new_product_default_code": "ABCDE012345",
                "copy_route": True,
                "copy_putaway": True,
            }
        )
        self.assertEqual(wiz.orderpoint_ids, self.orderpoint)
        new_product_id = wiz.button_validate().get("res_id")
        new_product = self.env["product.product"].browse(new_product_id)

        self.assertEqual(new_product.name, "RM-01 Replacement")
        self.assertEqual(new_product.default_code, "ABCDE012345")
        self.assertEqual(new_product.route_ids, self.old_product.route_ids)

        new_product_putaways = [
            (p.putaway_id, p.fixed_location_id) for p in new_product.product_putaway_ids
        ]
        for putaway in self.old_product.product_putaway_ids:
            putaway_tuple = (putaway.putaway_id, putaway.fixed_location_id)
            self.assertIn(putaway_tuple, new_product_putaways)

        self.assertEqual(self.orderpoint.product_id, new_product)
        self.assertIn(self.old_product, self.orderpoint.demand_product_ids)
