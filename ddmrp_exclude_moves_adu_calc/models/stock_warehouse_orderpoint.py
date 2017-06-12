# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp import api, models


class StockWarehouseOrderpoint(models.Model):
    _inherit = "stock.warehouse.orderpoint"

    @api.model
    def _exclude_past_moves_domain(self, locations):
        return [('exclude_from_adu', '=', True), ('state', '=', 'done')]

    @api.model
    def _past_moves_domain(self, date_from, locations):

        exclude_locs = self.env['stock.location'].search([(
            'exclude_from_adu', '=', True)])
        new_locs = self.env['stock.location']
        for loc in locations:
            if loc not in exclude_locs:
                new_locs += loc
        res = super(StockWarehouseOrderpoint,
                    self)._past_moves_domain(date_from, new_locs)
        exclude_moves = self.env['stock.move'].search(
            self._exclude_past_moves_domain(new_locs))
        res.append(('id', 'not in', exclude_moves.ids))
        return res
