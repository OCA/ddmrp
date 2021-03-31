# Copyright 2020-21 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields

from odoo.addons.ddmrp.tests.common import TestDdmrpCommon


class TestBufferCapacityLimit(TestDdmrpCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.uom_dozen = cls.env.ref("uom.product_uom_dozen")

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

    def test_02_storage_limit_and_qty_multiple(self):
        self.buffer_a.qty_multiple = 50
        self.assertEqual(self.buffer_a.top_of_green, 90)
        self.assertEqual(self.buffer_a.net_flow_position, 200)
        date_move = fields.Datetime.now()
        p_out_1 = self.create_pickingoutA(date_move, 180)
        p_out_1.action_confirm()
        self.buffer_a.cron_actions()
        self.assertEqual(self.buffer_a.net_flow_position, 20)
        # 70 adjusted by qty multiple to 100
        self.assertEqual(self.buffer_a.procure_recommended_qty, 100)
        self.buffer_a.storage_capacity_limit = 310
        self.buffer_a.cron_actions()
        # 70 unadjusted, 110 more to reach limit, adjusted to 100 because
        # 100 is possible
        self.assertEqual(self.buffer_a.procure_recommended_qty, 100)
        self.buffer_a.storage_capacity_limit = 275
        self.buffer_a.cron_actions()
        # 70 unadjusted, 75 more to reach limit, adjusted to 50 because
        # 100 is not possible
        self.assertEqual(self.buffer_a.procure_recommended_qty, 50)
        self.buffer_a.storage_capacity_limit = 240
        self.buffer_a.cron_actions()
        # 70 unadjusted, 40 more to reach limit, adjusted to 0 because
        # 50 is not possible
        self.assertEqual(self.buffer_a.procure_recommended_qty, 0)

    def test_03_storage_limit_and_qty_multiple_uom(self):
        self.buffer_a.qty_multiple = 2
        self.buffer_a.procure_uom_id = self.uom_dozen
        self.assertEqual(self.buffer_a.top_of_green, 90)
        self.assertEqual(self.buffer_a.net_flow_position, 200)
        date_move = fields.Datetime.now()
        p_out_1 = self.create_pickingoutA(date_move, 180)
        p_out_1.action_confirm()
        self.buffer_a.cron_actions()
        self.assertEqual(self.buffer_a.net_flow_position, 20)
        # 70 units adjusted by qty multiple and uom to 6 dozens.
        self.assertEqual(self.buffer_a.procure_recommended_qty, 6)
        self.buffer_a.storage_capacity_limit = 310
        self.buffer_a.cron_actions()
        # 70 unadjusted, 110 more to reach limit (9.5 dozens), adjusted to 6
        # dozens because it is a valid proposal.
        self.assertEqual(self.buffer_a.procure_recommended_qty, 6)
        self.buffer_a.storage_capacity_limit = 265
        self.buffer_a.cron_actions()
        # 70 unadjusted, 65 more to reach limit (5.4 dozens), adjusted to 4
        # dozens because 6 is not possible.
        self.assertEqual(self.buffer_a.procure_recommended_qty, 4)
        self.buffer_a.storage_capacity_limit = 223
        self.buffer_a.cron_actions()
        # 70 unadjusted, 23 more to reach limit (1.9 dozens), adjusted to 0
        # because the limit is less than the multiple of 2 dozens.
        self.assertEqual(self.buffer_a.procure_recommended_qty, 0)
