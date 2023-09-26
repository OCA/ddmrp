# Copyright 2023 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    def _get_domain_buffer_link_alternative(self):
        self.ensure_one()
        if not self.product_id:
            # Return impossible domain -> no buffer.
            return [(0, "=", 1)]
        return [
            ("product_id", "=", self.product_id.id),
            ("company_id", "=", self.order_id.company_id.id),
            ("item_type_alternative", "=", "purchased"),
            ("warehouse_id", "=", self.order_id.picking_type_id.warehouse_id.id),
        ]

    def _find_buffer_link(self):
        res = super()._find_buffer_link()
        buffer_model = self.env["stock.buffer"]
        move_model = self.env["stock.move"]
        for rec in self.filtered(lambda r: not r.buffer_ids):
            mto_move = move_model.search(
                [("created_purchase_line_id", "=", rec.id)], limit=1
            )
            if mto_move:
                # MTO lines are not accounted in MTS stock buffers.
                continue
            domain = rec._get_domain_buffer_link_alternative()
            buffer = buffer_model.search(domain, limit=1)
            if buffer:
                rec.buffer_ids = buffer
                rec._calc_execution_priority()
        return res
