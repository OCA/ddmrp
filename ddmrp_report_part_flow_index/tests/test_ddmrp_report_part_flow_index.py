# Copyright 2025 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo.tests import TransactionCase


class TestDDMRPReportPartFlowIndex(TransactionCase):
    def setUp(self):
        super().setUp()
        self.buffer_profile_mmm = self.env.ref(
            "ddmrp.stock_buffer_profile_replenish_manufactured_medium_medium"
        )
        self.stock_location = self.env.ref("stock.stock_location_stock")
        self.warehouse = self.env.ref("stock.warehouse0")
        self.adu_fixed = self.env.ref("ddmrp.adu_calculation_method_fixed")
        self.product = self.env["product.product"].create(
            {
                "name": "product test",
                "is_storable": True,
            }
        )
        self.buffer = self.env["stock.buffer"].create(
            {
                "buffer_profile_id": self.buffer_profile_mmm.id,
                "product_id": self.product.id,
                "location_id": self.stock_location.id,
                "warehouse_id": self.warehouse.id,
                "adu_calculation_method": self.adu_fixed.id,
                "adu_fixed": 4.0,
                "order_cycle": 5,
            }
        )
        self.flow_index_group_1 = self.env["ddmrp.flow.index.group"].create(
            {"name": "Group 1", "lower_range": 1, "upper_range": 10, "sequence": 0}
        )
        self.flow_index_group_2 = self.env["ddmrp.flow.index.group"].create(
            {"name": "Group 2", "lower_range": 11, "upper_range": 30, "sequence": 1}
        )

    def test_01_calc_flow_index_group_id(self):
        """Check if the flow_index_group_id of one buffer is correctly calculated"""

        self.buffer.cron_actions()
        self.assertEqual(
            self.buffer.flow_index_group_id,
            self.flow_index_group_1,
            "Flow index group was not updated correctly!",
        )
        self.buffer.order_cycle = 20
        self.env.invalidate_all()
        # Command needed to update report
        self.buffer.cron_actions()
        self.assertEqual(
            self.buffer.flow_index_group_id,
            self.flow_index_group_2,
            "Flow index group was not updated correctly!",
        )
