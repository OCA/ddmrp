# Copyright 2026 Camptocamp
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import models


class StockRule(models.Model):
    _inherit = "stock.rule"

    def _run_manufacture(self, procurements):
        # Refreshing the buffer inline locks it for the whole procurement
        # transaction, which conflicts with concurrent buffer updates
        return super(
            StockRule, self.with_context(auto_delay_ddmrp_cron_actions=True)
        )._run_manufacture(procurements)
