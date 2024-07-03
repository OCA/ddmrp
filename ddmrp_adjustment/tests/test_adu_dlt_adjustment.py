# Copyright 2018 Camptocamp SA
# Copyright 2020 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from .test_common import TestDDMRPAdjustmentCommon


class TestAduAdjustment(TestDDMRPAdjustmentCommon):
    def setUp(self):
        super().setUp()
        self.env["stock.buffer"].cron_ddmrp_adu()
        self.buffer._compute_dlt()
        self.adu_before = self.buffer.adu
        self.dlt_before = self.buffer.dlt

    def test_adu_adjustment(self):
        wiz = self._create_adjustment_wizard(1)
        wiz.apply_daf = True
        wiz.action_refresh()

        values = {
            getattr(self, "month_%i_%i" % (self.now.year, self.now.month)): 1.5,
        }
        for line in wiz.line_ids:
            line.value = values.get(line.date_range_id)
        wiz.button_validate()

        self.env["stock.buffer"].cron_ddmrp_adu()

        self.assertEqual(self.buffer.adu, self.adu_before * 1.5)

    def test_dlt_adjustment(self):
        wiz = self._create_adjustment_wizard(1)
        wiz.apply_ltaf = True
        wiz.action_refresh()

        values = {
            getattr(self, "month_%i_%i" % (self.now.year, self.now.month)): 2,
        }
        for line in wiz.line_ids:
            line.value = values.get(line.date_range_id)
        wiz.button_validate()

        self.buffer._compute_dlt()

        self.assertEqual(self.buffer.dlt, self.dlt_before * 2)

    def test_dummy(self):
        # Run actions
        self.assertTrue(self.buffer.action_view_demand_to_components())
        self.assertTrue(self.buffer.action_view_affecting_adu())
        self.assertTrue(self.buffer.action_view_parent_affecting_adu())
