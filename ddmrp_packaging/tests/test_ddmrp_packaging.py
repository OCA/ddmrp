# Copyright 2020 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo.exceptions import ValidationError
from odoo.tests.common import Form

from odoo.addons.ddmrp.tests.test_distributed_max_proc_time import TestDdmrpMaxProcTime


class TestDdmrpPackaging(TestDdmrpMaxProcTime):
    def setUp(self):
        super().setUp()
        self.buffer1 = self.env.ref("ddmrp.stock_buffer_fp01")
        self.buffer2 = self.env.ref("ddmrp.stock_buffer_rm01")

        self.packaging1 = self.env["product.packaging"].create(
            {
                "name": "Test Packaging",
                "product_id": self.buffer1.product_id.id,
                "qty": 10,
            }
        )
        self.packaging2 = self.env["product.packaging"].create(
            {
                "name": "Test Packaging",
                "product_id": self.buffer2.product_id.id,
                "qty": 10,
            }
        )
        self.packaging3 = self.env["product.packaging"].create(
            {
                "name": "Test Packaging",
                "product_id": self.buffer_dist.product_id.id,
                "qty": 10,
            }
        )

    def test_ddmrp_packaging(self):
        self.assertEqual(self.buffer1.qty_multiple, 1)
        self.assertEqual(self.buffer2.qty_multiple, 1)
        with self.assertRaises(ValidationError):
            self.buffer1.write({"packaging_id": self.packaging2.id})

        buffer_form = Form(self.buffer2)
        buffer_form.packaging_id = self.packaging2
        buffer_form.package_multiple = 10
        self.buffer2 = buffer_form.save()
        self.assertEqual(self.buffer2.qty_multiple, 100)

        buffer_form = Form(self.buffer2)
        buffer_form.packaging_id = self.packaging1
        buffer_form.package_multiple = 3.3

        self.buffer1.write(
            {
                "packaging_id": self.packaging1.id,
                "package_multiple": 10,
            }
        )
        self.assertEqual(self.buffer1.qty_multiple, 100)

        self.buffer_dist.procure_recommended_qty = 10000
        self.buffer_dist.packaging_id = self.packaging3.id
        self.buffer_dist.package_multiple = 10
        wizard = self.make_procurement_wiz.with_context(
            active_model="stock.buffer",
            active_ids=self.buffer_dist.ids,
            active_id=self.buffer_dist.id,
        ).create({})
        wizard.make_procurement()
        moves = self.env["stock.move"].search(
            [("product_id", "=", self.buffer_dist.product_id.id)]
        )
        self.assertEqual(moves.mapped("product_packaging_id").ids, self.packaging3.ids)
