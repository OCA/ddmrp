# Copyright 2023 ForgeFlow S.L. (http://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class MrpBomChangeLocation(models.TransientModel):
    _name = "mrp.bom.change.location"
    _description = "MRP Bom Change Location"

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        bom_obj = self.env["mrp.bom"]
        bom_id = self.env.context.get("active_id", False)
        active_model = self.env.context["active_model"]

        if not bom_id:
            return
        assert active_model == "mrp.bom", "Bad context propagation"

        bom = bom_obj.browse(bom_id)
        res.update(
            {
                "location_id": bom.context_location_id.id,
            }
        )
        return res

    location_id = fields.Many2one(
        comodel_name="stock.location",
    )

    def action_change_location(self):
        bom_id = self.env.context.get("active_id", False)
        return {
            "type": "ir.actions.act_window",
            "res_model": "mrp.bom",
            "view_mode": "form",
            "res_id": bom_id,
            "context": {
                "location_id": self.location_id.id,
                "warehouse_id": self.location_id.warehouse_id.id,
            },
        }
