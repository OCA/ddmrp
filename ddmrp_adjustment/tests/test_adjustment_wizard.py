# Copyright 2018 Camptocamp SA
# Copyright 2020 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from dateutil.relativedelta import relativedelta

from .test_common import TestDDMRPAdjustmentCommon


class TestAdjustmentWizard(TestDDMRPAdjustmentCommon):
    def test_adjustment_generation(self):
        wiz = self._create_adjustment_wizard(3)
        self.assertEqual(len(wiz.line_ids), 0)
        wiz.apply_daf = True
        wiz.apply_ltaf = True
        wiz.action_refresh()
        self.assertEqual(len(wiz.line_ids), 6)

        next_month = self.now + relativedelta(months=1)
        following_month = self.now + relativedelta(months=2)
        values = {
            "DAF": {
                getattr(self, "month_%i_%i" % (self.now.year, self.now.month)): 1.5,
                getattr(self, "month_%i_%i" % (next_month.year, next_month.month)): 2,
                getattr(
                    self, "month_%i_%i" % (following_month.year, following_month.month)
                ): 1.8,
            },
            "LTAF": {
                getattr(self, "month_%i_%i" % (self.now.year, self.now.month)): 2,
                getattr(self, "month_%i_%i" % (next_month.year, next_month.month)): 2.5,
                getattr(
                    self, "month_%i_%i" % (following_month.year, following_month.month)
                ): 2,
            },
        }
        for line in wiz.line_ids:
            line.value = values.get(line.factor).get(line.date_range_id)

        demand_adjustment_ids = wiz.button_validate().get("domain")[0][2]
        self.assertEqual(len(demand_adjustment_ids), 6)
        adjustments = self.env["ddmrp.adjustment"].browse(demand_adjustment_ids)
        for adj in adjustments:
            self.assertEqual(adj.buffer_id, self.buffer)
            if adj.adjustment_type == "DAF":
                self.assertEqual(adj.value, values.get("DAF").get(adj.date_range_id))
            if adj.adjustment_type == "LTAF":
                self.assertEqual(adj.value, values.get("LTAF").get(adj.date_range_id))
