# Copyright 2017-19 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models

DAF_string = "DAF"
LTAF_string = "LTAF"


class DdmrpAdjustment(models.Model):
    _name = "ddmrp.adjustment"

    buffer_id = fields.Many2one(
        comodel_name="stock.warehouse.orderpoint", string="Buffer",
        required=True,
    )
    product_id = fields.Many2one(
        comodel_name="product.product", related="buffer_id.product_id",
        readonly=True,
    )
    location_id = fields.Many2one(
        comodel_name="stock.location", related="buffer_id.location_id",
        readonly=True,
    )
    date_range_id = fields.Many2one(
        comodel_name="date.range", string="Date Range", required=True,
    )
    adjustment_type = fields.Selection(
        selection=[(DAF_string, 'Demand Adjustment Factor'),
                   (LTAF_string, 'Lead Time Adjustment Factor')],
    )
    value = fields.Float()
    company_id = fields.Many2one(
        comodel_name='res.company', string='Company', required=True,
        default=lambda self: self.env['res.company']._company_default_get(
            'ddmrp.adjustment'),
    )
