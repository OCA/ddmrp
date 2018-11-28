# Copyright 2017-18 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class StockWarehouseOrderpoint(models.Model):
    _inherit = "stock.warehouse.orderpoint"

    @api.model
    def _exclude_past_moves_domain(self):
        return [('exclude_from_adu', '=', True)]

    @api.model
    def _past_moves_domain(self, date_from, date_to, locations):
        new_locs = locations.filtered(lambda l: not l.exclude_from_adu)
        res = super(StockWarehouseOrderpoint,
                    self)._past_moves_domain(date_from, date_to, new_locs)
        exclude_moves = self.env['stock.move'].search(
            self._exclude_past_moves_domain())
        if exclude_moves:
            res.append(('id', 'not in', exclude_moves.ids))
        return res
