from odoo.addons.ddmrp_product_replace.tests.test_product_replace import (
    TestDDMRPProductReplace,
)


class TestDDMRPPackagingProductReplace(TestDDMRPProductReplace):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.replacement_product = cls.env.ref("ddmrp.product_product_rm02")
        cls.packaging1 = cls.env["product.packaging"].create(
            {"name": "Packaging Test 1", "product_id": cls.buffer.product_id.id}
        )
        cls.buffer.packaging_id = cls.packaging1.id

    def test_product_replace_packaging(self):
        """Check replacement product with packaging on buffers."""
        wiz = self.env["ddmrp.product.replace"].create(
            {
                "mode": "new_buffer",
                "old_product_ids": [(6, 0, self.buffer.product_id.ids)],
                "use_existing": "existing",
                "new_product_id": self.replacement_product.id,
            }
        )
        self.assertEqual(wiz.buffer_ids, self.buffer)
        self.assertFalse(wiz.is_already_replaced)
        res = wiz.button_validate()
        new_buffer_ids = res.get("domain")[0][2]
        model = res.get("res_model")
        self.assertEqual(model, "stock.buffer")
        new_buffer = self.bufferModel.browse(new_buffer_ids)
        self.assertEqual(len(new_buffer), 1)
        self.assertNotEqual(self.buffer.id, new_buffer.id)
        self.assertFalse(new_buffer.packaging_id)
