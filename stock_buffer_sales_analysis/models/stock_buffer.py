# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class StockBuffer(models.Model):
    _inherit = "stock.buffer"

    product_uom_name = fields.Char(
        "Unit of Measure Name", related="product_uom.name", readonly=True
    )
    product_id_sales_count = fields.Float(
        "Sold", related="product_id.sales_count", readonly=True
    )
    product_id_sale_ok = fields.Boolean(
        "Can be Sold", related="product_id.sale_ok", readonly=True
    )

    def action_view_sales(self):
        self.ensure_one()
        action = self.product_id.action_view_sales()
        action["domain"] = [("product_id", "=", self.product_id.id)]
        action["context"]["active_id"] = self.product_id.id
        return action
