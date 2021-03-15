# Copyright 2017-21 ForgeFlow (http://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, models


class StockBuffer(models.Model):
    _inherit = "stock.buffer"

    @api.model
    def _exclude_past_moves_domain(self):
        return [("exclude_from_adu", "=", True)]

    @api.model
    def _past_moves_domain(self, date_from, date_to, locations):
        new_locs = locations.filtered(lambda l: not l.exclude_from_adu)
        res = super()._past_moves_domain(date_from, date_to, new_locs)
        exclude_moves = self.env["stock.move"].search(self._exclude_past_moves_domain())
        if exclude_moves:
            res.append(("id", "not in", exclude_moves.ids))
        return res
