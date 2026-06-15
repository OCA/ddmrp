# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo.tests.common import TransactionCase


class TestDDMRPPurchaseHideOnhandStatus(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        vendor = cls.env["res.partner"].create({"name": "Test Vendor"})
        product = cls.env["product.product"].create(
            {
                "name": "Test Product",
                "is_storable": True,
            }
        )
        cls.po = cls.env["purchase.order"].create({"partner_id": vendor.id})
        cls.env["purchase.order.line"].create(
            {
                "order_id": cls.po.id,
                "product_id": product.id,
                "product_qty": 5.0,
            }
        )

    def test_ddmrp_purchase_hide_onhand_status(self):
        value = self.po.action_ddmrp_line_details()
        self.assertTrue(value)
