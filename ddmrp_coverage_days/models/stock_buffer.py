# Copyright 2020 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models
from odoo.tools import float_round


class Buffer(models.Model):
    _inherit = "stock.buffer"

    coverage_days = fields.Float(compute="_compute_coverage_days")

    def _compute_coverage_days(self):
        for rec in self:
            if rec.adu != 0:
                rec.coverage_days = float_round(
                    rec.product_location_qty_available_not_res / rec.adu,
                    precision_rounding=rec.product_id.uom_id.rounding,
                )
            else:
                rec.coverage_days = 0
