# Copyright 2017-20 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class DdmrpAdjustmentDemand(models.Model):
    _name = "ddmrp.adjustment.demand"
    _description = "DDMRP Adjustment Demand"

    buffer_id = fields.Many2one(
        comodel_name="stock.buffer",
        string="Apply to",
    )
    product_id = fields.Many2one(related="buffer_id.product_id")
    buffer_origin_id = fields.Many2one(
        comodel_name="stock.buffer",
        string="Originated from",
        required=True,
        ondelete="cascade",
    )
    product_origin_id = fields.Many2one(
        related="buffer_origin_id.product_id",
        string="Origin Product",
    )
    extra_demand = fields.Float()
    product_uom_id = fields.Many2one(
        comodel_name="uom.uom",
        string="Unit of Measure",
        related="buffer_id.product_uom",
    )
    date_start = fields.Date(
        string="Start date",
    )
    date_end = fields.Date(
        string="End date",
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        related="buffer_id.company_id",
    )
