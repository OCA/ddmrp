# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    # Override to make '_compute_product_available_qty' method of
    # 'stock.buffer' more efficient.
    state = fields.Selection(index=True)
