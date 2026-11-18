# Copyright 2026 Ledoent
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo.addons.ddmrp.tests.common import TestDdmrpCommon


class TestDdmrpChatter(TestDdmrpCommon):
    def test_chatter_wired_on_buffer(self):
        """stock.buffer carries the mail mixins and tracked fields."""
        buffer = self.buffer_a
        self.assertIn("message_ids", buffer._fields)
        self.assertIn("activity_ids", buffer._fields)
        for fname in (
            "product_id",
            "buffer_profile_id",
            "adu_calculation_method",
            "qty_multiple",
            "auto_procure",
        ):
            self.assertTrue(
                buffer._fields[fname].tracking, f"{fname} should be tracked"
            )
