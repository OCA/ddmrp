# Copyright 2020 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class Buffer(models.Model):
    _inherit = "stock.buffer"

    coverage_days = fields.Float(
        compute="_compute_coverage_days", string="Days of Coverage"
    )

    def _compute_coverage_days(self):
        for rec in self:
            if rec.adu != 0:
                rec.coverage_days = rec.product_id.uom_id.round(
                    rec.product_location_qty_available_not_res / rec.adu
                )
            else:
                rec.coverage_days = 0
