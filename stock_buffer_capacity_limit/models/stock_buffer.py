# Copyright 2020 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class StockBuffer(models.Model):
    _inherit = "stock.buffer"

    storage_capacity_limit = fields.Float(
        digits="Product Unit of Measure",
        help="The system will never propose a procurement that would move "
        "on-hand qty (considering short-term incoming qty as well) over "
        "this limit, even if this means that you have planning or "
        "execution alerts.",
    )

    @api.depends("storage_capacity_limit")
    def _compute_procure_recommended_qty(self):
        res = super()._compute_procure_recommended_qty()
        for rec in self.filtered(lambda b: b.storage_capacity_limit > 0.0):
            recommendation_limit = max(
                rec.storage_capacity_limit
                - rec.product_id.qty_available
                - rec.incoming_dlt_qty,
                0,
            )
            qty = min(rec.procure_recommended_qty, recommendation_limit)
            rec.procure_recommended_qty = qty
        return res
