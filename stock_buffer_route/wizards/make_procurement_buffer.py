# Copyright 2023 ForgeFlow S.L. (http://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class MakeProcurementBuffer(models.TransientModel):
    _inherit = "make.procurement.buffer"

    partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Vendor",
        help="If set, will be used as preferred vendor for purchase routes.",
    )
    item_ids = fields.One2many(
        comodel_name="make.procurement.buffer.item",
        inverse_name="wiz_id",
        string="Items",
    )

    @api.model
    def _prepare_item(self, buffer, qty_override=None):
        res = super(MakeProcurementBuffer, self)._prepare_item(buffer, qty_override)
        res["route_ids"] = buffer.route_ids.ids
        res["route_id"] = buffer.route_id.id
        return res


class MakeProcurementBufferItem(models.TransientModel):
    _inherit = "make.procurement.buffer.item"

    route_ids = fields.Many2many(
        "stock.location.route",
        string="Allowed routes",
    )
    route_id = fields.Many2one(
        "stock.location.route",
        domain="[('id', 'in', route_ids)]",
    )

    def _prepare_values_make_procurement(self):
        values = super()._prepare_values_make_procurement()
        values.update({"route_ids": self.route_id})
        return values
