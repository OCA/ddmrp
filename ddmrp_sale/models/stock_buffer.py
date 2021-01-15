# Copyright 2021 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class StockBuffer(models.Model):
    _inherit = "stock.buffer"

    can_serve_sales = fields.Boolean(compute="_compute_can_serve_sales", store=True,)

    def _get_sale_source_location(self):
        self.ensure_one()
        proc_loc = self.env.ref("stock.stock_location_customers")
        values = {
            "warehouse_id": self.warehouse_id,
            "company_id": self.company_id,
        }
        rule = self.env["procurement.group"]._get_rule(
            self.product_id, proc_loc, values
        )
        return rule and rule.location_src_id

    @api.depends("warehouse_id", "location_id")
    def _compute_can_serve_sales(self):
        for rec in self:
            loc = rec._get_sale_source_location()
            rec.can_serve_sales = loc.is_sublocation_of(rec.location_id)

    def _search_sales_qualified_demand_domain(self):
        self.ensure_one()
        horizon = self.order_spike_horizon
        date_to = self.warehouse_id.wh_plan_days(fields.Datetime.now(), horizon)
        return [
            ("product_id", "=", self.product_id.id),
            ("state", "in", ["draft", "sent"],),
            ("commitment_date", "<=", date_to),
            ("order_id.warehouse_id", "=", self.warehouse_id.id),
            ("move_ids", "=", False),
        ]

    def _search_sales_qualified_demand(self):
        domain = self._search_sales_qualified_demand_domain()
        so_lines = self.env["sale.order.line"].search(domain)
        return so_lines

    def _get_demand_by_days(self):
        demand_by_days = super()._get_demand_by_days()
        if self.can_serve_sales:
            so_lines = self._search_sales_qualified_demand()

            sol_dates = [dt.date() for dt in so_lines.mapped("commitment_date")]
            for d in sol_dates:
                if not demand_by_days.get(d):
                    demand_by_days[d] = 0.0
            for sol in so_lines:
                date = sol.commitment_date.date()
                demand_by_days[date] += sol.product_uom._compute_quantity(
                    sol.product_uom_qty, sol.product_id.uom_id
                )
        return demand_by_days
