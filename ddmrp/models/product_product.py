# Copyright 2020 ForgeFlow S.L. (http://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class Product(models.Model):
    _inherit = "product.product"

    buffer_ids = fields.One2many(
        comodel_name="stock.buffer",
        string="Stock Buffers",
        inverse_name="product_id",
    )

    def write(self, values):
        res = super().write(values)
        if values.get("active") is False:
            buffers = (
                self.env["stock.buffer"].sudo().search([("product_id", "in", self.ids)])
            )
            buffers.write({"active": False})
        return res
