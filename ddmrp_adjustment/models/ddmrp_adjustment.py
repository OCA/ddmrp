# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models


class DdmrpAdjustment(models.Model):
    _name = "ddmrp.adjustment"

    buffer_id = fields.Many2one(
        comodel_name="stock.warehouse.orderpoint", string="Buffer",
        required=True)
    product_id = fields.Many2one(
        comodel_name="product.product", related="buffer_id.product_id",
        readonly=True)
    location_id = fields.Many2one(
        comodel_name="stock.location", related="buffer_id.location_id",
        readonly=True)
    date_range_id = fields.Many2one(
        comodel_name="date.range", string="Date Range", required=True)
    daf = fields.Float(
        string="DAF", help="Demand Adjustment Factor", default=0.0)
    company_id = fields.Many2one(
        comodel_name='res.company', string='Company', required=True,
        default=lambda self: self.env['res.company']._company_default_get(
            'ddmrp.adjustment'))
