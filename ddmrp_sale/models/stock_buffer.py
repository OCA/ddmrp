# Copyright 2021-26 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class StockBuffer(models.Model):
    _inherit = "stock.buffer"

    can_serve_sales = fields.Boolean(
        compute="_compute_can_serve_sales",
        store=True,
    )
    qualified_demand_sale_order_line_ids = fields.Many2many(
        comodel_name="sale.order.line",
    )

    def _get_sale_source_location(self, proc_locs):
        # Adapting this method to be very similar to _get_source_location_from_route
        # from stock_helper but not using that as it disappears in future versions and
        # we don't want to add dependency to the new module.
        self.ensure_one()
        values = {
            "warehouse_id": self.warehouse_id,
            "company_id": self.company_id,
        }
        sale_source_locations = self.env["stock.location"]
        for proc_loc in proc_locs:
            current_location = proc_loc
            while current_location:
                rule = self.env["procurement.group"]._get_rule(
                    self.product_id, current_location, values
                )
                if not rule:
                    break
                if rule.procure_method == "make_to_stock":
                    sale_source_locations |= rule.location_src_id
                    break
                if rule.location_src_id == current_location:
                    break
                current_location = rule.location_src_id
        return sale_source_locations

    @api.depends("warehouse_id", "location_id")
    def _compute_can_serve_sales(self):
        proc_locations = self.env["stock.location"].search([("usage", "=", "customer")])
        for rec in self:
            locs = rec._get_sale_source_location(proc_locations)
            rec.can_serve_sales = any(
                [loc.is_sublocation_of(rec.location_id) for loc in locs]
            )

    def _search_sales_qualified_demand_domain(self):
        self.ensure_one()
        horizon = self.order_spike_horizon
        date_to = self.warehouse_id.wh_plan_days(fields.Datetime.now(), horizon)
        return [
            ("product_id", "=", self.product_id.id),
            (
                "state",
                "in",
                ["draft", "sent"],
            ),
            ("order_id.commitment_date", "<=", date_to),
            ("order_id.warehouse_id", "=", self.warehouse_id.id),
        ]

    def _search_sales_qualified_demand(self):
        domain = self._search_sales_qualified_demand_domain()
        so_lines = self.env["sale.order.line"].search(domain)
        return so_lines

    def _get_sol_date(self, sol):
        """Return the date to use for a sale order line in DDMRP demand calculation."""
        return sol.order_id.commitment_date

    def _get_so_lines_by_days(self, so_lines):
        so_lines_by_days = {}
        sol_dates = [self._get_sol_date(sol).date() for sol in so_lines]
        for d in sol_dates:
            if not so_lines_by_days.get(d):
                so_lines_by_days[d] = 0.0
        for sol in so_lines:
            date = self._get_sol_date(sol).date()
            so_lines_by_days[date] += sol.product_uom._compute_quantity(
                sol.product_uom_qty, sol.product_id.uom_id
            )
        return so_lines_by_days

    def _calc_qualified_demand(self, current_date=False):
        res = super()._calc_qualified_demand(current_date)
        today = current_date or fields.date.today()
        for rec in self:
            if rec.can_serve_sales:
                qualified_demand = 0.0
                lines = rec._search_sales_qualified_demand()
                so_lines_by_days = rec._get_so_lines_by_days(lines)
                dates = list(set(so_lines_by_days.keys()))
                for date in dates:
                    if (
                        so_lines_by_days.get(date, 0.0) >= rec.order_spike_threshold
                        or date <= today
                    ):
                        qualified_demand += so_lines_by_days.get(date, 0.0)
                    else:
                        lines = lines.filtered(
                            lambda x: rec._get_sol_date(x).date() != date
                        )
                rec.qualified_demand += qualified_demand
                rec.qualified_demand_sale_order_line_ids = lines
        return res

    def action_view_qualified_demand_so_lines(self):
        lines = self.qualified_demand_sale_order_line_ids
        action = self.env.ref("sale.action_quotations")
        result = action.read()[0]
        result["context"] = {}
        result["domain"] = [("id", "in", lines.mapped("order_id.id"))]
        return result
