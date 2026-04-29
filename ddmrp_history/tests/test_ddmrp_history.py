# Copyright 2018 Camptocamp SA
# Copyright 2019 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from datetime import datetime, timedelta

from odoo import fields

from odoo.addons.ddmrp.tests.common import TestDdmrpCommon


class TestDDMRPHistory(TestDdmrpCommon):
    def test_history(self):
        self.buffer_purchase.write(
            {"adu_fixed": 10, "order_cycle": 5, "order_spike_horizon": 10}
        )
        self.buffer_purchase.cron_actions()
        history_today = self.env["ddmrp.history"].search(
            [("buffer_id", "=", self.buffer_purchase.id)], order="id desc", limit=1
        )
        self.assertTrue(history_today)
        self.assertAlmostEqual(
            fields.Datetime.from_string(history_today.date),
            datetime.today(),
            delta=timedelta(seconds=1),
        )
        self.assertEqual(history_today.top_of_red, self.buffer_purchase.top_of_red)
        self.assertEqual(
            history_today.top_of_yellow, self.buffer_purchase.top_of_yellow
        )
        self.assertEqual(history_today.top_of_green, self.buffer_purchase.top_of_green)
        # Check that chart computation do not raise an error:
        self.buffer_purchase.cron_actions()
        self.assertTrue(self.buffer_purchase.planning_history_chart)
        self.assertTrue(self.buffer_purchase.execution_history_chart)
