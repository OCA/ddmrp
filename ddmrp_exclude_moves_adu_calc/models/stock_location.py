# Copyright 2017-21 ForgeFlow (http://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class StockLocation(models.Model):
    _inherit = "stock.location"

    exclude_from_adu = fields.Boolean(
        string="Exclude this location from ADU calculation",
        copy=False,
        help="If this flag is set stock moves into this location will be "
        "excluded from ADU calculation in the origin location buffer.",
    )
