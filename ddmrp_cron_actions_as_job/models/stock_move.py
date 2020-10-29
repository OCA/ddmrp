# Copyright 2020 Camptocamp
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _update_ddmrp_nfp(self):
        return super(
            StockMove, self.with_context(auto_delay_ddmrp_cron_actions=True)
        )._update_ddmrp_nfp()
