# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime

from odoo.tests import TransactionCase
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class TestDDMRPHistory(TransactionCase):

    def setUp(self):
        super().setUp()
        self.orderpoint = self.env.ref('ddmrp.stock_warehouse_orderpoint_901p')

    def test_history(self):
        self.orderpoint.write({
            'adu_fixed': 10,
            'order_cycle': 5,
            'order_spike_horizon': 10
        })
        self.orderpoint.cron_actions()
        history_today = self.env['ddmrp.history'].search([
            ('orderpoint_id', '=', self.orderpoint.id)],
            order='date desc', limit=1
        )
        self.assertEqual(history_today.date, datetime.today().strftime(
            DEFAULT_SERVER_DATETIME_FORMAT))
        self.assertEqual(history_today.top_of_red,
                         self.orderpoint.top_of_red)
        self.assertEqual(history_today.top_of_yellow,
                         self.orderpoint.top_of_yellow)
        self.assertEqual(history_today.top_of_green,
                         self.orderpoint.top_of_green)
