# Copyright 2018 Camptocamp SA
# Copyright 2019 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from datetime import datetime, timedelta

from odoo import fields
from odoo.tests import TransactionCase


class TestDDMRPHistory(TransactionCase):
    def setUp(self):
        super().setUp()
        self.buffer = self.env.ref("ddmrp.stock_buffer_fp01")

    def test_history(self):
        self.buffer.write(
            {"adu_fixed": 10, "order_cycle": 5, "order_spike_horizon": 10}
        )
        self.buffer.cron_actions()
        history_today = self.env["ddmrp.history"].search(
            [("buffer_id", "=", self.buffer.id)], order="date desc", limit=1
        )
        self.assertAlmostEqual(
            fields.Datetime.from_string(history_today.date),
            datetime.today(),
            delta=timedelta(seconds=1),
        )
        self.assertEqual(history_today.top_of_red, self.buffer.top_of_red)
        self.assertEqual(history_today.top_of_yellow, self.buffer.top_of_yellow)
        self.assertEqual(history_today.top_of_green, self.buffer.top_of_green)
        # Check that chart computation do not raise an error:
        self.buffer.cron_actions()
        self.assertTrue(self.buffer.planning_history_chart)
        self.assertTrue(self.buffer.execution_history_chart)
