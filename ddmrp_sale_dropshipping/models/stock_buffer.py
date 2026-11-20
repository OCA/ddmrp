# Copyright 2024 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import models


class StockBuffer(models.Model):
    _inherit = "stock.buffer"

    def _search_sales_qualified_demand_base_domain(self):
        res = super()._search_sales_qualified_demand_base_domain()
        dropship_pick_types = self.env["stock.picking.type"].search(
            [
                ("default_location_src_id.usage", "=", "supplier"),
                ("default_location_dest_id.usage", "=", "customer"),
                ("company_id", "=", self.company_id.id),
            ]
        )
        dropship_routes = (
            self.env["stock.rule"]
            .search([("picking_type_id", "in", dropship_pick_types.ids)])
            .mapped("route_id")
        )
        if dropship_routes:
            res += [
                "|",
                ("route_id", "=", False),
                ("route_id", "not in", dropship_routes.ids),
            ]
        return res
