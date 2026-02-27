# Copyright 2018 Camptocamp SA
# Copyright 2020-26 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from calendar import monthrange

from .test_common import TestDDMRPAdjustmentCommon


class TestAduAdjustment(TestDDMRPAdjustmentCommon):
    def setUp(self):
        super().setUp()
        self.env["stock.buffer"].cron_ddmrp_adu()
        self.buffer._compute_dlt()
        self.buffer._compute_red_zone()
        self.buffer._compute_yellow_zone()
        self.buffer._compute_green_zone()
        self.adu_before = self.buffer.adu
        self.dlt_before = self.buffer.dlt
        self.red_zone_qty_before = self.buffer.red_zone_qty
        self.yellow_zone_qty_before = self.buffer.yellow_zone_qty
        self.green_zone_qty_before = self.buffer.green_zone_qty
        self.current_month = getattr(
            self, "month_%i_%i" % (self.now.year, self.now.month)
        )

    def test_adu_adjustment(self):
        self.env["ddmrp.adjustment"].create(
            {
                "buffer_id": self.buffer.id,
                "date_range_id": self.current_month.id,
                "adjustment_type": "DAF",
                "value": 1.5,
            }
        )
        self.env["stock.buffer"].cron_ddmrp_adu()
        self.assertEqual(self.buffer.adu, self.adu_before * 1.5)

    def test_dlt_adjustment(self):
        self.env["ddmrp.adjustment"].create(
            {
                "buffer_id": self.buffer.id,
                "date_range_id": self.current_month.id,
                "adjustment_type": "LTAF",
                "value": 2,
            }
        )
        self.buffer._compute_dlt()
        self.assertEqual(self.buffer.dlt, self.dlt_before * 2)

    def test_red_zone_adjustment(self):
        self.env["ddmrp.adjustment"].create(
            {
                "buffer_id": self.buffer.id,
                "date_range_id": self.current_month.id,
                "adjustment_type": "RZAF",
                "value": 1.5,
            }
        )
        self.buffer._compute_red_zone()
        self.assertEqual(self.buffer.red_zone_qty, self.red_zone_qty_before * 1.5)

    def test_yellow_zone_adjustment(self):
        self.env["ddmrp.adjustment"].create(
            {
                "buffer_id": self.buffer.id,
                "date_range_id": self.current_month.id,
                "adjustment_type": "YZAF",
                "value": 1.5,
            }
        )
        self.buffer._compute_yellow_zone()
        self.assertEqual(self.buffer.yellow_zone_qty, self.yellow_zone_qty_before * 1.5)

    def test_green_zone_adjustment(self):
        self.env["ddmrp.adjustment"].create(
            {
                "buffer_id": self.buffer.id,
                "date_range_id": self.current_month.id,
                "adjustment_type": "GZAF",
                "value": 1.5,
            }
        )
        self.buffer._compute_green_zone()
        self.assertEqual(self.buffer.green_zone_qty, self.green_zone_qty_before * 1.5)

    def test_manual_date_adjustment(self):
        """Test that adjustments work with manual dates instead of date ranges."""
        today = self.now.date()
        adj = self.env["ddmrp.adjustment"].create(
            {
                "buffer_id": self.buffer.id,
                "adjustment_type": "DAF",
                "value": 1.5,
                "manual_date_start": today.replace(day=1),
                "manual_date_end": today.replace(
                    day=monthrange(today.year, today.month)[1]
                ),
            }
        )
        # Verify computed dates
        self.assertEqual(adj.date_start, today.replace(day=1))
        self.assertEqual(
            adj.date_end,
            today.replace(day=monthrange(today.year, today.month)[1]),
        )
        self.assertFalse(adj.date_range_id)
        # Verify adjustment is applied
        self.env["stock.buffer"].cron_ddmrp_adu()
        self.assertEqual(self.buffer.adu, self.adu_before * 1.5)

    def test_dummy(self):
        # Run actions
        self.assertTrue(self.buffer.action_view_demand_to_components())
        self.assertTrue(self.buffer.action_view_affecting_adu())
        self.assertTrue(self.buffer.action_view_parent_affecting_adu())
