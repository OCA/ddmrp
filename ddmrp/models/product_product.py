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

    buffer_count = fields.Integer(compute="_compute_buffer_count")

    def write(self, values):
        res = super().write(values)
        if values.get("active") is False:
            buffers = (
                self.env["stock.buffer"].sudo().search([("product_id", "in", self.ids)])
            )
            buffers.write({"active": False})
        return res

    def _compute_buffer_count(self):
        for rec in self:
            rec.buffer_count = len(rec.buffer_ids)

    def action_view_stock_buffers(self):
        action = self.env["ir.actions.actions"]._for_xml_id("ddmrp.action_stock_buffer")
        action["context"] = {}
        action["domain"] = [("id", "in", self.buffer_ids.ids)]
        return action
