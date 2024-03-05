# Copyright 2017-24 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models

DAF_string = "DAF"
LTAF_string = "LTAF"


class DdmrpAdjustment(models.Model):
    _name = "ddmrp.adjustment"
    _description = "DDMRP Adjustment"

    buffer_id = fields.Many2one(
        comodel_name="stock.buffer",
        string="Buffer",
        required=True,
    )
    product_id = fields.Many2one(
        comodel_name="product.product",
        related="buffer_id.product_id",
        readonly=True,
    )
    location_id = fields.Many2one(
        comodel_name="stock.location",
        related="buffer_id.location_id",
        readonly=True,
    )
    date_range_id = fields.Many2one(
        comodel_name="date.range",
        string="Date Range",
        required=True,
    )
    adjustment_type = fields.Selection(
        selection=[
            (DAF_string, "Demand Adjustment Factor"),
            (LTAF_string, "Lead Time Adjustment Factor"),
        ],
    )
    value = fields.Float(group_operator="avg")
    company_id = fields.Many2one(
        comodel_name="res.company",
        related="buffer_id.company_id",
    )
    date_start = fields.Date(related="date_range_id.date_start")
    date_end = fields.Date(related="date_range_id.date_end")
