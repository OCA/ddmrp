# Copyright 2023 ForgeFlow S.L. (http://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class DdmrpDuplicateBuffer(models.TransientModel):
    _name = "ddmrp.duplicate.buffer"
    _description = "DDMRP Duplicate Buffer"

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        buffer_obj = self.env["stock.buffer"]
        buffer_ids = self.env.context.get("active_ids", [])
        active_model = self.env.context["active_model"]

        if not buffer_ids:
            return
        assert active_model == "stock.buffer", "Bad context propagation"

        if len(buffer_ids) > 1:
            res.update(
                {
                    "type": "location",
                }
            )
        else:
            buffer = buffer_obj.browse(buffer_ids)
            res.update(
                {
                    "type": "both",
                    "product_id": buffer.product_id.id,
                    "location_id": buffer.location_id.id,
                }
            )
        return res

    type = fields.Selection(
        string="Duplication Type",
        selection=[
            ("both", "Change both values"),
            ("product", "Change Product"),
            ("location", "Change Location"),
        ],
        required=True,
    )
    product_id = fields.Many2one(
        comodel_name="product.product",
        string="New Product",
    )
    location_id = fields.Many2one(
        comodel_name="stock.location",
        string="New Location",
    )

    def action_duplicate_buffer(self):
        buffer_obj = self.env["stock.buffer"]
        buffer_ids = self.env.context["active_ids"] or []

        if self.type in ["product", "both"] and not self.product_id:
            raise UserError(_("Please select a New Product."))
        if self.type in ["location", "both"] and not self.location_id:
            raise UserError(_("Please select a New Location."))

        copy_buffers = self.env["stock.buffer"]
        for buffer in buffer_obj.browse(buffer_ids):
            default = {}
            if self.type in ["product", "both"]:
                default["product_id"] = self.product_id.id
            if self.type in ["location", "both"]:
                default["location_id"] = self.location_id.id
            copy_buffers |= buffer.copy(default)

        return {
            "type": "ir.actions.act_window",
            "name": _("Duplicated Buffers"),
            "res_model": "stock.buffer",
            "view_mode": "tree,form",
            "domain": [("id", "in", copy_buffers.ids)],
        }
