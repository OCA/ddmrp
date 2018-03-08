# Copyright 2017-18 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class DdmrpAdjustmentDemand(models.Model):
    _name = "ddmrp.adjustment.demand"

    buffer_id = fields.Many2one(
        comodel_name="stock.warehouse.orderpoint", string="Apply to",
    )
    product_id = fields.Many2one(related="buffer_id.product_id")
    buffer_origin_id = fields.Many2one(
        comodel_name="stock.warehouse.orderpoint", string="Originated from",
    )
    product_origin_id = fields.Many2one(related="buffer_origin_id.product_id")
    extra_demand = fields.Float(string="Extra Demand")
    product_uom_id = fields.Many2one(
        comodel_name="product.uom", string="Unit of Measure",
        related="buffer_id.product_uom",
    )
    date_start = fields.Date(
        string='Start date',
    )
    date_end = fields.Date(
        string='End date',
    )

    # TODO: everything READONLY?
