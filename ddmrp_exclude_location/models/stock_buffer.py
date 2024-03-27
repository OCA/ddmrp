# Copyright 2023 ForgeFlow (http://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from collections import defaultdict

from odoo import api, fields, models


class StockBuffer(models.Model):
    _inherit = "stock.buffer"

    exclude_location_ids = fields.Many2many(
        comodel_name="stock.location",
        string="Exclude Locations",
        compute="_compute_exclude_location_ids",
        store=True,
        readonly=False,
    )

    @api.depends("location_id")
    def _compute_exclude_location_ids(self):
        for rec in self:
            locations = (
                self.env["stock.location"]
                .with_context(active_test=False)
                .search([("id", "child_of", rec.location_id.ids)])
            )
            rec.exclude_location_ids = locations.filtered(
                lambda l: l.exclude_from_ddmrp
            )

    @api.model
    def _demand_estimate_domain(self, locations, date_from, date_to):
        new_locs = locations.filtered(lambda l: not l.exclude_from_ddmrp)
        res = super()._demand_estimate_domain(new_locs, date_from, date_to)
        return res

    def _get_exclude_outgoing_reservation_qty(self):
        """Return the qty reserved in operations that move products outside
        of the buffer exclude location in the UoM of the product."""
        domain = [
            ("product_id", "=", self.product_id.id),
            ("state", "in", ("partially_available", "assigned")),
        ]
        lines = self.env["stock.move.line"].search(domain)
        lines = lines.filtered(
            lambda line: line.location_id.is_sublocation_of(self.exclude_location_ids)
            and not line.location_dest_id.is_sublocation_of(self.exclude_location_ids)
        )
        return sum(lines.mapped("product_qty"))

    def _compute_product_available_qty(self):
        res = super()._compute_product_available_qty()
        operation_by_location = defaultdict(lambda: self.env["stock.buffer"])
        for rec in self:
            for exclude_location_id in rec.exclude_location_ids:
                operation_by_location[exclude_location_id] |= rec
        for location_id, buffer_in_location in operation_by_location.items():
            products = (
                buffer_in_location.mapped("product_id")
                .with_context(location=location_id.id)
                ._compute_quantities_dict(
                    lot_id=self.env.context.get("lot_id"),
                    owner_id=self.env.context.get("owner_id"),
                    package_id=self.env.context.get("package_id"),
                )
            )
            for buffer in buffer_in_location:
                product = products[buffer.product_id.id]
                reserved_qty = buffer._get_exclude_outgoing_reservation_qty()
                qty_available_not_res = buffer.product_location_qty_available_not_res
                buffer.update(
                    {
                        "product_location_qty": buffer.product_location_qty
                        - product["qty_available"],
                        "product_location_qty_available_not_res": qty_available_not_res
                        - product["qty_available"]
                        + reserved_qty,
                    }
                )
        return res

    def _search_open_stock_moves_domain(self):
        res = super()._search_open_stock_moves_domain()
        return res + [
            ("!"),
            ("location_dest_id", "child_of", self.exclude_location_ids.ids),
        ]

    @api.model
    def _past_moves_domain(self, date_from, date_to, locations):
        new_locs = locations.filtered(lambda l: not l.exclude_from_ddmrp)
        res = super()._past_moves_domain(date_from, date_to, new_locs)
        return res

    @api.model
    def _future_moves_domain(self, date_from, date_to, locations):
        new_locs = locations.filtered(lambda l: not l.exclude_from_ddmrp)
        res = super()._future_moves_domain(date_from, date_to, new_locs)
        return res

    def _search_stock_moves_qualified_demand(self):
        res = super()._search_stock_moves_qualified_demand()
        domain = self._search_stock_moves_qualified_demand_domain()
        moves = self.env["stock.move"].search(domain)
        moves = moves.filtered(
            lambda move: move.location_id.is_sublocation_of(self.location_id)
            and not move.location_id.is_sublocation_of(self.exclude_location_ids)
            and move.location_dest_id.is_sublocation_of(self.exclude_location_ids)
        )
        return moves + res.filtered(
            lambda move: not move.location_id.is_sublocation_of(
                self.exclude_location_ids
            )
        )

    def _search_stock_moves_incoming(self, outside_dlt=False):
        res = super()._search_stock_moves_incoming(outside_dlt)
        domain = self._search_stock_moves_qualified_demand_domain()
        moves = self.env["stock.move"].search(domain)
        moves = moves.filtered(
            lambda move: move.location_id.is_sublocation_of(self.exclude_location_ids)
            and move.location_dest_id.is_sublocation_of(self.location_id)
            and not move.location_dest_id.is_sublocation_of(self.exclude_location_ids)
        )
        return moves + res.filtered(
            lambda move: not move.location_dest_id.is_sublocation_of(
                self.exclude_location_ids
            )
        )

    def _search_mrp_moves_qualified_demand(self):
        res = super()._search_mrp_moves_qualified_demand()
        return res.filtered(
            lambda move: not move.mrp_area_id.location_id.is_sublocation_of(
                self.exclude_location_ids
            )
        )
