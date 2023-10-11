# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def action_stock_buffer_open(self):
        """Open a stock.buffer list related to products of the stock.picking."""
        self.ensure_one()
        domain = [
            ("product_id", "in", self.mapped("move_ids.product_id.id")),
            ("company_id", "=", self.company_id.id),
        ]
        action = self.env["ir.actions.actions"]._for_xml_id("ddmrp.action_stock_buffer")
        action["domain"] = domain
        action["context"] = {"search_default_procure_recommended": 1}
        return action
