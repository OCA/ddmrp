# Copyright 2026 ForgeFlow S.L. (http://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields
from odoo.tests import tagged

from odoo.addons.ddmrp.tests.common import TestDdmrpCommon


@tagged("post_install", "-at_install")
class TestDDMRPPurchaseApproved(TestDdmrpCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.po_model = cls.env["purchase.order"]
        cls.pol_model = cls.env["purchase.order.line"]
        cls.vendor = cls.partner_model.create({"name": "Test Vendor Approved"})

    def _create_po_line(self, qty=10.0, state="draft"):
        po = self.po_model.create({"partner_id": self.vendor.id})
        pol = self.pol_model.create(
            {
                "order_id": po.id,
                "product_id": self.product_purchased.id,
                "product_qty": qty,
                "product_uom": self.product_purchased.uom_id.id,
                "price_unit": 100.0,
                "date_planned": fields.Datetime.now(),
                "name": "Test",
            }
        )
        if state != "draft":
            po.write({"state": state})
        return po, pol

    def test_01_approved_in_purchase_order_states(self):
        """The 'approved' state must be included in DDMRP PO states."""
        states = self.buffer_purchase._get_unconfirmed_po_states()
        self.assertIn("approved", states)

    def test_02_buffer_rfq_qty_through_state_transitions(self):
        """Full lifecycle: draft -> approved -> purchase.
        RFQ qty must reflect the PO only in draft/approved states."""
        buf = self.buffer_purchase
        buf.cron_actions()
        self.assertEqual(buf.rfq_total_qty, 0.0)

        po, pol = self._create_po_line(qty=25.0, state="draft")
        buf.cron_actions()
        self.assertEqual(buf.rfq_total_qty, 25.0)

        po.write({"state": "approved"})
        buf.cron_actions()
        self.assertEqual(buf.rfq_total_qty, 25.0)

        po.write({"state": "purchase"})
        buf.cron_actions()
        self.assertEqual(buf.rfq_total_qty, 0.0)
