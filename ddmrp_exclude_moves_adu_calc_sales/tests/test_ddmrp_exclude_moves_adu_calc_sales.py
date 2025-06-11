# Copyright 2024 ForgeFlow (http://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).


import odoo.tests.common as common


class TestDdmrp(common.TransactionCase):
    def setUp(self):
        super().setUp()

        # Models
        self.productModel = self.env["product.product"]
        self.bufferModel = self.env["stock.buffer"]

        # Refs
        self.main_company = self.env.ref("base.main_company")
        self.warehouse = self.env.ref("stock.warehouse0")
        self.stock_location = self.env.ref("stock.stock_location_stock")
        self.uom_unit = self.env.ref("uom.product_uom_unit")
        self.buffer_profile_pur = self.env.ref(
            "ddmrp.stock_buffer_profile_replenish_purchased_short_low"
        )

        self.product_a = self.productModel.create(
            {
                "name": "product A",
                "standard_price": 1,
                "is_storable": True,
                "uom_id": self.uom_unit.id,
                "default_code": "A",
            }
        )

        self.customer = self.env["res.partner"].create(
            {
                "name": "Caroline Customer",
                "email": "customer@example.com",
            }
        )

    def create_sale_order(self):
        return self.env["sale.order"].create(
            {
                "partner_id": self.customer.id,
                "order_line": [
                    (0, 0, ope)
                    for ope in [
                        {
                            "name": p.name,
                            "product_id": p.id,
                            "product_uom_qty": 2,
                            "product_uom": p.uom_id.id,
                            "price_unit": 10,
                        }
                        for p in self.product_a
                    ]
                ],
            }
        )

    def test_01_exclude_so_from_adu(self):
        method = self.env.ref("ddmrp.adu_calculation_method_past_120")
        self.bufferModel.create(
            {
                "buffer_profile_id": self.buffer_profile_pur.id,
                "product_id": self.product_a.id,
                "location_id": self.stock_location.id,
                "warehouse_id": self.warehouse.id,
                "qty_multiple": 0.0,
                "dlt": 10,
                "adu_calculation_method": method.id,
                "adu_fixed": 4,
            }
        )
        so = self.create_sale_order()
        so.action_confirm()
        self.assertFalse(so.order_line.exclude_from_adu)
        self.assertFalse(so.picking_ids.move_ids.exclude_from_adu)
        so.order_line.write({"exclude_from_adu": True})
        self.assertTrue(so.order_line.exclude_from_adu)
        self.assertTrue(so.picking_ids.move_ids.exclude_from_adu)
        so.picking_ids.move_ids._toggle_exclude_from_adu()
        so.order_line.invalidate_recordset()
        self.assertFalse(so.order_line.exclude_from_adu)
        self.assertFalse(so.picking_ids.move_ids.exclude_from_adu)
