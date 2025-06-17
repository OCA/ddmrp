# Copyright 2025 ForgeFlow S.L. (http://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).


from odoo import fields, models


class StockBuffer(models.Model):
    _inherit = "stock.buffer"

    product_categ_id = fields.Many2one(
        comodel_name="product.category",
        string="Product Category",
        related="product_id.categ_id",
        store=True,
        readonly=True,
    )
