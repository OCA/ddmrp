# -*- coding: utf-8 -*-
# Copyright 2017-18 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    exclude_from_adu = fields.Boolean(
        string='Exclude this move from ADU calculation', copy=False,
        help="If this flag is set this stock move will be excluded from ADU "
             "calculation",
    )
