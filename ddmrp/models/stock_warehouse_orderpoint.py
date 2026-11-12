# Copyright 2024 ForgeFlow S.L. (http://www.forgeflow.com)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, models


class StockWarehouseOrderpoint(models.Model):
    _inherit = "stock.warehouse.orderpoint"

    def _get_orderpoint_action(self):
        return super(
            StockWarehouseOrderpoint, self.with_context(_from_get_op_action=True)
        )._get_orderpoint_action()

    @api.model_create_multi
    def create(self, vals_list):
        if self.env.context.get("_from_get_op_action"):
            new_vals_list = []
            for vals in vals_list:
                buffer = self.env["stock.buffer"].search(
                    [
                        ("product_id", "=", vals.get("product_id")),
                        ("location_id", "=", vals.get("location_id")),
                    ],
                    limit=1,
                )
                if not buffer:
                    new_vals_list.append(vals)
            vals_list = new_vals_list
        return super().create(vals_list)
