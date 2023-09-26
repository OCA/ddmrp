# Copyright 2023 ForgeFlow S.L. (http://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models

_ITEM_TYPES = [
    ("manufactured", "Manufactured"),
    ("purchased", "Purchased"),
    ("distributed", "Distributed"),
]


class MakeProcurementBuffer(models.TransientModel):
    _inherit = "make.procurement.buffer"

    @api.model
    def _prepare_item(self, buffer, qty_override=None):
        res = super(MakeProcurementBuffer, self)._prepare_item(buffer, qty_override)
        res["route_ids"] = buffer.route_ids.ids
        res["route_id"] = buffer.route_id.id
        context = {
            "route_id": buffer.route_id,
            "item_type_alternative": buffer.item_type_alternative,
        }
        res["date_planned"] = buffer.with_context(**context)._get_date_planned()
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
    item_type_alternative = fields.Selection(
        string="Alternative Item Type",
        selection=_ITEM_TYPES,
        compute="_compute_item_type_alternative",
        store=True,
    )

    @api.onchange("route_id")
    def _onchange_route_id(self):
        for rec in self:
            context = {
                "route_id": rec.route_id,
                "item_type_alternative": rec.item_type_alternative,
            }
            rec.date_planned = rec.buffer_id.with_context(**context)._get_date_planned()

    @api.depends("route_id", "route_id.rule_ids", "route_id.rule_ids.action")
    def _compute_item_type_alternative(self):
        for rec in self:
            rec.item_type_alternative = ""
            if rec.route_id:
                if "buy" in rec.route_id.mapped("rule_ids.action"):
                    rec.item_type_alternative = "purchased"
                elif "manufacture" in rec.route_id.mapped("rule_ids.action"):
                    rec.item_type_alternative = "manufactured"
                elif "pull" in rec.route_id.mapped(
                    "rule_ids.action"
                ) or "pull_push" in rec.route_id.mapped("rule_ids.action"):
                    rec.item_type_alternative = "distributed"

    def _prepare_values_make_procurement(self):
        values = super()._prepare_values_make_procurement()
        values.update({"route_ids": self.route_id})
        return values
