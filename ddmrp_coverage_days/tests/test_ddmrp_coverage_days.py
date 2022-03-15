# Copyright 2020 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

import odoo.tests.common as common


class TestDdmrpCoverageDays(common.TransactionCase):
    def setUp(self):
        super().setUp()

        # Models
        self.productModel = self.env["product.product"]
        self.bufferModel = self.env["stock.buffer"]
        self.quantModel = self.env["stock.quant"]
        self.locationModel = self.env["stock.location"]
        self.adumethodModel = self.env["product.adu.calculation.method"]

        # Refs
        self.main_company = self.env.ref("base.main_company")
        self.warehouse = self.env.ref("stock.warehouse0")
        self.stock_location = self.env.ref("stock.stock_location_stock")
        self.uom_unit = self.env.ref("uom.product_uom_unit")
        self.uom_unit.rounding = 1
        purchase_route = self.env.ref("purchase_stock.route_warehouse0_buy")

        self.productA = self.productModel.create(
            {
                "name": "product A",
                "standard_price": 100.0,
                "weight": 2.0,
                "type": "product",
                "uom_id": self.uom_unit.id,
                "default_code": "A",
                "route_ids": [(6, 0, purchase_route.ids)],
            }
        )

        self.quantModel.create(
            {
                "location_id": self.stock_location.id,
                "company_id": self.main_company.id,
                "product_id": self.productA.id,
                "quantity": 650,
            }
        )

        # Create Buffers:
        self.method_fixed = self.env.ref("ddmrp.adu_calculation_method_fixed")
        self.buffer_profile_override = self.env.ref(
            "ddmrp.stock_buffer_profile_replenish_override_purchased_short_low"
        )
        self.buffer_a = self.bufferModel.create(
            {
                "buffer_profile_id": self.buffer_profile_override.id,
                "green_override": 150.0,
                "yellow_override": 30.0,
                "red_override": 20.0,
                "product_id": self.productA.id,
                "location_id": self.stock_location.id,
                "warehouse_id": self.warehouse.id,
                "adu_calculation_method": self.method_fixed.id,
                "adu_fixed": 10.0,
                "order_spike_horizon": 8,
                "minimum_order_quantity": 20,
            }
        )

    def test_01_coverage_days(self):
        self.buffer_a.write({"adu_fixed": 16.0})
        # Coverage days= Quantity OH/ADU = 650/16=41
        self.assertEqual(self.buffer_a.coverage_days, 41)
