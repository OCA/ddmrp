# Copyright 2020 ForgeFlow S.L. (http://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class Product(models.Model):
    _inherit = "product.product"

    buffer_ids = fields.One2many(
        comodel_name="stock.buffer", string="Stock Buffers", inverse_name="product_id",
    )

    def write(self, values):
        res = super().write(values)
        if "active" in values:
            buffers = self.env["stock.buffer"].search(
                [
                    ("product_id", "in", self.ids),
                    "|",
                    ("active", "=", True),
                    ("active", "=", False),
                ]
            )
            buffers.write({"active": values.get("active")})
        return res
