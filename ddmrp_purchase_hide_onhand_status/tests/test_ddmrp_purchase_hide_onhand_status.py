# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo.tests.common import SavepointCase


class TestDDMRPPurchaseHideOnhandStatus(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.po = cls.env.ref("purchase.purchase_order_1")

    def test_ddmrp_purchase_hide_onhand_status(self):
        value = self.po.action_ddmrp_line_details()
        self.assertTrue(value)
