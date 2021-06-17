# Copyright 2019-20 ForgeFlow S.L. (https://www.forgeflow.com)
# Copyright 2019-20 Camptocamp SA
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class StockBuffer(models.Model):
    _inherit = "stock.buffer"

    route_ids = fields.Many2many(
        "stock.location.route",
        string="Allowed routes",
        compute="_compute_route_ids",
    )
    route_id = fields.Many2one(
        "stock.location.route",
        string="Route",
        domain="[('id', 'in', route_ids)]",
        ondelete="restrict",
    )

    @api.depends("product_id", "warehouse_id", "warehouse_id.route_ids", "location_id")
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
            or any(rule.action == "buy" for rule in route.rule_ids)
        )

    def get_parents(self):
        location = self.location_id
        result = location
        while location.location_id:
            location = location.location_id
            result |= location
        return result

    def _prepare_procurement_values(self, product_qty, date=False, group=False):
        res = super()._prepare_procurement_values(product_qty, date=date, group=group)
        res["route_ids"] = self.route_id
        return res

    def _values_source_location_from_route(self):
        values = super()._values_source_location_from_route()
        if self.route_id:
            values["route_ids"] = self.route_id
        return values

    def write(self, vals):
        res = super().write(vals)
        if "route_id" in vals:
            self._calc_distributed_source_location()
        return res
