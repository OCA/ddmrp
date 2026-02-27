# Copyright 2017-26 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

DAF_string = "DAF"
LTAF_string = "LTAF"
RZAF_string = "RZAF"
YZAF_string = "YZAF"
GZAF_string = "GZAF"


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
    )
    manual_date_start = fields.Date(string="Start Date (Manual)")
    manual_date_end = fields.Date(string="End Date (Manual)")
    adjustment_type = fields.Selection(
        selection=[
            (DAF_string, "Demand Adjustment Factor"),
            (LTAF_string, "Lead Time Adjustment Factor"),
            (RZAF_string, "Red Zone Adjustment Factor"),
            (YZAF_string, "Yellow Zone Adjustment Factor"),
            (GZAF_string, "Green Zone Adjustment Factor"),
        ],
        required=True,
    )
    value = fields.Float(aggregator="avg")
    company_id = fields.Many2one(
        comodel_name="res.company",
        related="buffer_id.company_id",
    )
    date_start = fields.Date(string="Start Date", compute="_compute_dates", store=True)
    date_end = fields.Date(string="End date", compute="_compute_dates", store=True)

    @api.depends(
        "date_range_id",
        "date_range_id.date_start",
        "date_range_id.date_end",
        "manual_date_start",
        "manual_date_end",
    )
    def _compute_dates(self):
        for rec in self:
            if rec.date_range_id:
                rec.date_start = rec.date_range_id.date_start
                rec.date_end = rec.date_range_id.date_end
            else:
                rec.date_start = rec.manual_date_start
                rec.date_end = rec.manual_date_end

    @api.constrains("date_start", "date_end")
    def _check_dates_required(self):
        for rec in self:
            if not rec.date_start or not rec.date_end:
                raise ValidationError(
                    _(
                        "You must either set a Date Range or provide"
                        " manual Date From/Date To."
                    )
                )

    @api.constrains("value")
    def _check_value_positive(self):
        for rec in self:
            if rec.value < 0:
                raise ValidationError(_("Adjustment value must be positive."))
