# Copyright 2019-20 ForgeFlow S.L. (http://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = "product.template"

    buffer_count = fields.Integer(compute="_compute_buffer_count")

    def _compute_buffer_count(self):
        for rec in self:
            rec.buffer_count = sum(
                variant.buffer_count for variant in rec.product_variant_ids
            )

    # UOM: (stock_orderpoint_uom):
    @api.constrains("uom_id")
    def _check_buffer_procure_uom(self):
        for rec in self:
            buffers = self.env["stock.buffer"].search(
                [
                    ("product_id", "in", rec.product_variant_ids.ids),
                ],
            )
            uom_id = rec.uom_id
            incompatible = buffers.filtered(
                lambda b, uom_id=uom_id: b.procure_uom_id
                and not b.procure_uom_id._compute_quantity(
                    1.0, uom_id, raise_if_failure=False
                )
            )
            if incompatible:
                raise ValidationError(
                    rec.env._(
                        "At least one stock buffer for this product has a "
                        "different Procurement unit of measure category."
                    )
                )

    def action_view_stock_buffers(self):
        return self.product_variant_ids.action_view_stock_buffers()
