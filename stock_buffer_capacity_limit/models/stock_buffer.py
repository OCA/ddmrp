# Copyright 2020 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models
from odoo.tools import float_compare


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
                rec.storage_capacity_limit  # UoM of the product
                - rec.product_location_qty
                - rec.incoming_dlt_qty,
                0,
            )
            if rec.procure_uom_id:
                rounding = rec.procure_uom_id.rounding
                limit_uom = rec.product_id.uom_id._compute_quantity(
                    recommendation_limit, rec.procure_uom_id
                )
            else:
                rounding = rec.product_uom.rounding
                limit_uom = recommendation_limit

            if (
                float_compare(
                    limit_uom, rec.procure_recommended_qty, precision_rounding=rounding
                )
                > 0
            ):
                # Recommendation is valid.
                continue

            new_recommendation = limit_uom
            if (
                float_compare(
                    rec.procure_min_qty, limit_uom, precision_rounding=rounding
                )
                > 0
            ):
                new_recommendation = 0
            elif rec.qty_multiple:
                new_recommendation -= new_recommendation % rec.qty_multiple
            rec.procure_recommended_qty = new_recommendation
        return res
