# Copyright 2017-18 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class StockLocation(models.Model):
    _inherit = "stock.location"

    exclude_from_adu = fields.Boolean(
        string='Exclude this location from ADU calculation', copy=False,
        help="If this flag is set stock moves into this location will be "
             "excluded from ADU calculation in the origin location buffer.",
    )
