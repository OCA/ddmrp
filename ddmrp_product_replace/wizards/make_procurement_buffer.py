# Copyright 2021 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import _, api, fields, models


class MakeProcurementBuffer(models.TransientModel):
    _inherit = "make.procurement.buffer"

    has_replaced_buffers = fields.Boolean(
        compute="_compute_replaced_by_alert_text",
    )
    replaced_by_alert_text = fields.Text(
        compute="_compute_replaced_by_alert_text",
    )

    @api.depends("item_ids")
    def _compute_replaced_by_alert_text(self):
        for rec in self:
            if any(r.buffer_id.replaced_by_id for r in rec.item_ids):
                rec.has_replaced_buffers = True
                alert_text = _("Some products are being replaced:")
                for item in rec.item_ids:
                    if item.buffer_id.replaced_by_id:
                        replacement = item.buffer_id.replaced_by_id
                        alert_text += (
                            f"\n - {item.buffer_id.display_name} "
                            f"({item.buffer_id.product_id.display_name}) "
                            f"replaced by {replacement.display_name} "
                            f"({replacement.product_id.display_name})"
                        )
                rec.replaced_by_alert_text = alert_text
            else:
                rec.has_replaced_buffers = False
                rec.replaced_by_alert_text = ""
