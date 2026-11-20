# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import models


class StockBuffer(models.Model):
    _inherit = "stock.buffer"

    def _search_sales_qualified_demand_base_domain(self):
        domain = super()._search_sales_qualified_demand_base_domain()
        new_domain = []
        for leaf in domain:
            if (
                isinstance(leaf, (list, tuple))
                and leaf[0] == "order_id.commitment_date"
            ):
                # Either the line has its own commitment_date within the horizon,
                # or the line has no commitment_date and the order's date is within horizon.
                new_domain += [
                    "|",
                    ("commitment_date", leaf[1], leaf[2]),
                    "&",
                    ("commitment_date", "=", False),
                    leaf,
                ]
            else:
                new_domain.append(leaf)
        return new_domain

    def _get_sol_date(self, sol):
        return sol.commitment_date or sol.order_id.commitment_date
