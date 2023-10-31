# Copyright 2023 ForgeFlow (http://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class StockLocation(models.Model):
    _inherit = "stock.location"

    exclude_from_ddmrp = fields.Boolean(
        string="Exclude this location from DDMRP",
        copy=False,
        help="If this flag is set, this location will be "
        "excluded from DDMRP Stock Buffers.",
        inverse="_inverse_exclude_from_ddmrp",
    )

    def _inverse_exclude_from_ddmrp(self):
        for rec in self:
            if rec.exclude_from_ddmrp:
                buffers = self.env["stock.buffer"].search([])
                for buffer in buffers:
                    if rec.is_sublocation_of(buffer.location_id):
                        buffer.exclude_location_ids |= rec
            else:
                buffers = self.env["stock.buffer"].search(
                    [("exclude_location_ids", "in", rec.ids)]
                )
                for buffer in buffers:
                    buffer.exclude_location_ids -= rec
