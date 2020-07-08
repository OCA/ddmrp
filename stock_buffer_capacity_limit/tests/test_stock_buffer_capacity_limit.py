# Copyright 2020 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields

from odoo.addons.ddmrp.tests.common import TestDdmrpCommon


class TestBufferCapacityLimit(TestDdmrpCommon):
    def test_01_storage_capacity_limit(self):
        self.assertEqual(self.buffer_a.top_of_green, 90)
        self.assertEqual(self.buffer_a.net_flow_position, 200)
        date_move = fields.Datetime.now()
        p_out_1 = self.create_pickingoutA(date_move, 170)
        p_out_1.action_confirm()
        self.buffer_a.cron_actions()
        self.assertEqual(self.buffer_a.net_flow_position, 30)
        self.assertEqual(self.buffer_a.procure_recommended_qty, 60)
        self.buffer_a.storage_capacity_limit = 210
        self.assertEqual(self.buffer_a.product_location_qty_available_not_res, 200)
        self.assertEqual(self.buffer_a.incoming_dlt_qty, 0)
        # Only 10 units left to reach storage limit: 210 - 200 - 0
        self.assertEqual(self.buffer_a.procure_recommended_qty, 10)
        # When we create the incoming picking, there is no space left.
        p_in_1 = self.create_pickinginA(date_move, 10)
        p_in_1.action_confirm()
        self.buffer_a.cron_actions()
        self.assertEqual(self.buffer_a.procure_recommended_qty, 0)
