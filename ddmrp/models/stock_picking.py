# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import models


class StockPickgin(models.Model):
    _inherit = "stock.picking"

    def action_stock_buffer_open(self):
        """Open a sock.buffer list related to products of the stock.picking."""
        self.ensure_one()
        domain = [
            ("product_id", "in", self.mapped("move_lines.product_id.id")),
            ("warehouse_id", "=", self.picking_type_id.warehouse_id.id),
            ("company_id", "=", self.company_id.id),
        ]
        return {
            "type": "ir.actions.act_window",
            "name": "Stock Buffers",
            "res_model": "stock.buffer",
            "view_mode": "tree,form",
            "domain": domain,
            "context": {"search_default_procure_recommended": 1},
        }
