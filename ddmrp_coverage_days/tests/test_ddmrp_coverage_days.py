# Copyright 2020 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

import odoo.tests.common as common


class TestDdmrpCoverageDays(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Models
        cls.productModel = cls.env["product.product"]
        cls.bufferModel = cls.env["stock.buffer"]
        cls.quantModel = cls.env["stock.quant"]
        cls.locationModel = cls.env["stock.location"]
        cls.adumethodModel = cls.env["product.adu.calculation.method"]

        # Refs
        cls.main_company = cls.env.ref("base.main_company")
        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.stock_location = cls.env.ref("stock.stock_location_stock")
        cls.uom_unit = cls.env.ref("uom.product_uom_unit")
        cls.uom_unit.rounding = 1
        purchase_route = cls.env.ref("purchase_stock.route_warehouse0_buy")

        cls.productA = cls.productModel.create(
            {
                "name": "product A",
                "standard_price": 100.0,
                "weight": 2.0,
                "type": "product",
                "uom_id": cls.uom_unit.id,
                "default_code": "A",
                "route_ids": [(6, 0, purchase_route.ids)],
            }
        )

        cls.quantModel.create(
            {
                "location_id": cls.stock_location.id,
                "company_id": cls.main_company.id,
                "product_id": cls.productA.id,
                "quantity": 650,
            }
        )

        # Create Buffers:
        cls.method_fixed = cls.env.ref("ddmrp.adu_calculation_method_fixed")
        cls.buffer_profile_override = cls.env.ref(
            "ddmrp.stock_buffer_profile_replenish_override_purchased_short_low"
        )
        cls.buffer_a = cls.bufferModel.create(
            {
                "buffer_profile_id": cls.buffer_profile_override.id,
                "green_override": 150.0,
                "yellow_override": 30.0,
                "red_override": 20.0,
                "product_id": cls.productA.id,
                "location_id": cls.stock_location.id,
                "warehouse_id": cls.warehouse.id,
                "adu_calculation_method": cls.method_fixed.id,
                "adu_fixed": 10.0,
                "order_spike_horizon": 8,
                "minimum_order_quantity": 20,
            }
        )

    def test_01_coverage_days(self):
        self.buffer_a.write({"adu_fixed": 16.0})
        # Coverage days= Quantity OH/ADU = 650/16=41
        self.assertEqual(self.buffer_a.coverage_days, 41)
