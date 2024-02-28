# Copyright 2024 ForgeFlow (http://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _toggle_exclude_from_adu(self):
        res = super()._toggle_exclude_from_adu()
        for sl in self.mapped("sale_line_id"):
            value = sl.move_ids.mapped("exclude_from_adu")
            if len(value) == 1:
                sl.exclude_from_adu = value[0]
        return res
