# Copyright 2026 Ledoent
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo.addons.ddmrp.tests.common import TestDdmrpCommon


class TestStockBufferSalesAnalysis(TestDdmrpCommon):
    def test_buffer_sales_fields_and_action(self):
        """Related sales fields resolve and the sales action targets the
        buffer's product."""
        buffer = self.buffer_a
        self.assertEqual(buffer.product_uom_name, buffer.product_id.uom_id.name)
        self.assertEqual(buffer.product_id_sale_ok, buffer.product_id.sale_ok)
        action = buffer.action_view_sales()
        self.assertEqual(action["domain"], [("product_id", "=", buffer.product_id.id)])
        self.assertEqual(action["context"]["active_id"], buffer.product_id.id)
