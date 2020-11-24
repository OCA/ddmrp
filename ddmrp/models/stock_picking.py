# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import models


class StockPickgin(models.Model):
    _inherit = "stock.picking"

    def action_stock_buffer_open(self):
        """Open a sock.buffer list related to products of the stock.picking."""
        product_ids = self.mapped("move_lines.product_id.id")
        return {
            "type": "ir.actions.act_window",
            "name": "Stock Buffers",
            "res_model": "stock.buffer",
            "view_mode": "tree,form",
            "domain": [("product_id", "in", product_ids)],
            "context": {"search_default_procure_recommended": 1},
        }
