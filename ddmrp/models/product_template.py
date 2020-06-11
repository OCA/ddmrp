# Copyright 2019-20 ForgeFlow S.L. (http://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import _, api, models
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = "product.template"

    # UOM: (stock_orderpoint_uom):
    @api.constrains("uom_id")
    def _check_buffer_procure_uom(self):
        for rec in self:
            buffer = self.env["stock.buffer"].search(
                [
                    ("procure_uom_id.category_id", "!=", rec.uom_id.category_id.id),
                    ("product_id", "in", rec.product_variant_ids.ids),
                ],
                limit=1,
            )
            if buffer:
                raise ValidationError(
                    _(
                        "At least one stock buffer for this product has a "
                        "different Procurement unit of measure category."
                    )
                )
