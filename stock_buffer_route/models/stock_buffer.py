# Copyright 2019-23 ForgeFlow S.L. (https://www.forgeflow.com)
# Copyright 2019-20 Camptocamp SA
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from datetime import datetime, timedelta

from odoo import api, fields, models
from odoo.tools import float_compare

_ITEM_TYPES = [
    ("manufactured", "Manufactured"),
    ("purchased", "Purchased"),
    ("distributed", "Distributed"),
]


class StockBuffer(models.Model):
    _inherit = "stock.buffer"

    route_ids = fields.Many2many(
        "stock.location.route",
        string="Allowed routes",
        compute="_compute_route_ids",
        store=True,
    )
    route_id = fields.Many2one(
        "stock.location.route",
        string="Route",
        domain="[('id', 'in', route_ids)]",
        ondelete="restrict",
    )
    item_type_alternative = fields.Selection(
        string="Alternative Item Type",
        selection=_ITEM_TYPES,
        compute="_compute_item_type_alternative",
        store=True,
    )
    dlt_alternative = fields.Float(
        string="Alternative DLT (days)",
        compute="_compute_dlt_alternative",
        help="Alternative Decoupled Lead Time (days)",
    )

    @api.depends("product_id", "location_id", "product_id.route_ids")
    def _compute_route_ids(self):
        route_obj = self.env["stock.location.route"]
        for record in self:
            wh_routes = record.warehouse_id.route_ids
            routes = route_obj.browse()
            if record.product_id:
                routes += record.product_id.mapped(
                    "route_ids"
                ) | record.product_id.mapped("categ_id").mapped("total_route_ids")
            if record.warehouse_id:
                routes |= wh_routes
            parents = record.get_parents()
            record.route_ids = self._get_location_routes_of_parents(routes, parents)

    @api.depends(
        "product_id", "route_id", "route_id.rule_ids", "route_id.rule_ids.action"
    )
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

    def _compute_dlt_alternative(self):
        for rec in self:
            route_id = self.env.context.get("route_id", rec.route_id)
            dlt = 0
            if route_id:
                item_type_alternative = self.env.context.get(
                    "item_type_alternative", rec.item_type_alternative
                )
                if item_type_alternative == "manufactured":
                    bom = rec._get_manufactured_bom()
                    dlt = bom.dlt
                elif item_type_alternative == "distributed":
                    dlt = rec.lead_days
                else:
                    sellers = rec._get_product_sellers()
                    dlt = sellers and fields.first(sellers).delay or rec.lead_days
            rec.dlt_alternative = dlt

    @api.depends(
        "buffer_profile_id",
        "item_type",
        "product_id.seller_ids",
        "product_id.seller_ids.company_id",
        "product_id.seller_ids.name",
        "product_id.seller_ids.product_id",
        "product_id.seller_ids.sequence",
        "product_id.seller_ids.min_qty",
        "product_id.seller_ids.price",
        "item_type_alternative",
    )
    def _compute_main_supplier(self):
        res = super()._compute_main_supplier()
        for rec in self:
            if rec.item_type_alternative == "purchased":
                suppliers = rec._get_product_sellers()
                rec.main_supplier_id = suppliers[0].name if suppliers else False
        return res

    def _get_rfq_dlt_qty(self, outside_dlt=False):
        res = super()._get_rfq_dlt_qty(outside_dlt)
        if self.item_type_alternative == "purchased":
            cut_date = self._get_incoming_supply_date_limit()
            if not outside_dlt:
                pols = self.purchase_line_ids.filtered(
                    lambda l: l.date_planned <= fields.Datetime.to_datetime(cut_date)
                    and l.state in ("draft", "sent")
                )
            else:
                pols = self.purchase_line_ids.filtered(
                    lambda l: l.date_planned > fields.Datetime.to_datetime(cut_date)
                    and l.order_id.state in ("draft", "sent")
                )
            res += sum(pols.mapped("product_qty"))
        return res

    def _get_date_planned(self, force_lt=None):
        res = super()._get_date_planned(force_lt)
        route_id = self.env.context.get("route_id", False)
        if route_id:
            dlt = int(self.dlt_alternative)
            item_type_alternative = self.env.context.get(
                "item_type_alternative", self.item_type_alternative
            )
            if self.warehouse_id.calendar_id and item_type_alternative != "purchased":
                res = self.warehouse_id.wh_plan_days(datetime.now(), dlt)
            else:
                res = fields.datetime.today() + timedelta(days=dlt)
        return res

    def _get_location_routes_of_parents(self, routes, parents):
        return routes.filtered(
            lambda route: (
                # at least one rule of the route must have a destination location
                # reaching the buffer
                route.rule_ids.filtered(lambda rule: rule.action != "push").mapped(
                    "location_id"
                )
                & parents
            )
        )

    def get_parents(self):
        location = self.location_id
        result = location
        while location.location_id:
            location = location.location_id
            result |= location
        return result

    def _values_source_location_from_route(self):
        values = super()._values_source_location_from_route()
        if self.route_id:
            values["route_ids"] = self.route_id
        return values

    def _calc_distributed_source_location(self):
        res = super()._calc_distributed_source_location()
        for record in self:
            if (
                not record.distributed_source_location_id
                and record.item_type_alternative != "distributed"
            ):
                source_location = record._source_location_from_route()
                record.distributed_source_location_id = source_location
        return res

    def _procure_qty_to_order(self):
        res = super()._procure_qty_to_order()
        qty_to_order = self.procure_recommended_qty
        rounding = self.procure_uom_id.rounding or self.product_uom.rounding
        if (
            self.item_type_alternative == "distributed"
            and self.buffer_profile_id.replenish_distributed_limit_to_free_qty
        ):
            if (
                float_compare(
                    self.distributed_source_location_qty,
                    self.procure_min_qty,
                    precision_rounding=rounding,
                )
                < 0
            ):
                res = 0
            else:
                res = min(qty_to_order, self.distributed_source_location_qty)
        return res

    def write(self, vals):
        res = super().write(vals)
        if "route_id" in vals:
            self._calc_distributed_source_location()
        return res

    def action_view_supply(self, outside_dlt=False):
        res = super().action_view_supply(outside_dlt)
        # If route is set it means that there is at least two alternatively ways to
        # procure the buffer. Therefore, we will show Stock Pickings.
        if self.route_id:
            moves = self._search_stock_moves_incoming(outside_dlt)
            picks = moves.mapped("picking_id")
            res = self.env["ir.actions.actions"]._for_xml_id(
                "stock.action_picking_tree_all"
            )
            res["context"] = {}
            res["domain"] = [("id", "in", picks.ids)]
        return res
