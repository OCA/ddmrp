# Copyright 2018 ForgeFlow S.L. (http://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, models


class MultiLevelMrp(models.TransientModel):
    _inherit = "mrp.multi.level"

    @api.model
    def _exclude_from_mrp(self, product, mrp_area):
        """Exclude from MRP scheduler products that are buffered."""
        res = super()._exclude_from_mrp(product, mrp_area)
        ddmrp = self.env["stock.buffer"].search(
            [
                ("location_id", "=", mrp_area.location_id.id),  # child of?
                ("product_id", "=", product.id),
            ]
        )
        if ddmrp and not self.env.context.get("mrp_explosion"):
            return True
        return res
