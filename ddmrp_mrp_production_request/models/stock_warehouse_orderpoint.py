# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class StockWarehouseOrderpoint(models.Model):
    _inherit = 'stock.warehouse.orderpoint'

    mrp_production_request_ids = fields.One2many(
        string='Manufacturing Requests', comodel_name='mrp.production.request',
        inverse_name='orderpoint_id')

    @api.multi
    def cron_actions(self):
        res = super(StockWarehouseOrderpoint, self).cron_actions()
        self.mrp_production_request_ids._calc_execution_priority()
        return res
