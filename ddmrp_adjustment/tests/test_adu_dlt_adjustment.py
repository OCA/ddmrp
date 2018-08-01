# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from .test_common import TestDDMRPAdjustmentCommon


class TestAduAdjustment(TestDDMRPAdjustmentCommon):

    def setUp(self):
        super().setUp()
        self.env['stock.warehouse.orderpoint'].cron_ddmrp_adu()
        self.orderpoint._compute_dlt()
        self.adu_before = self.orderpoint.adu
        self.dlt_before = self.orderpoint.dlt

    def test_adu_adjustment(self):
        wiz = self._create_adjustment_wizard(1)
        wiz.apply_daf = True
        wiz._onchange_sheet()

        values = {
            getattr(self, 'month_%i_%i' % (
                self.now.year, self.now.month)): 1.5,
        }
        for line in wiz.line_ids:
            line.value = values.get(line.date_range_id)
        wiz.button_validate()

        self.env['stock.warehouse.orderpoint'].cron_ddmrp_adu()

        self.assertEqual(self.orderpoint.adu, self.adu_before * 1.5)

    def test_dlt_adjustment(self):
        wiz = self._create_adjustment_wizard(1)
        wiz.apply_ltaf = True
        wiz._onchange_sheet()

        values = {
            getattr(self, 'month_%i_%i' % (
                self.now.year, self.now.month)): 2,
        }
        for line in wiz.line_ids:
            line.value = values.get(line.date_range_id)
        wiz.button_validate()

        self.orderpoint._compute_dlt()

        self.assertEqual(self.orderpoint.dlt, self.dlt_before * 2)
