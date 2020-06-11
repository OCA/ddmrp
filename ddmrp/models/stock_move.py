# Copyright 2019-20 ForgeFlow S.L. (http://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    buffer_ids = fields.Many2many(
        comodel_name="stock.buffer",
        string="Linked Stock Buffers",
    )

    def _prepare_procurement_values(self):
        res = super(StockMove, self)._prepare_procurement_values()
        if self.buffer_ids:
            res["buffer_ids"] = self.buffer_ids
        return res

    def _merge_moves_fields(self):
        res = super(StockMove, self)._merge_moves_fields()
        res["buffer_ids"] = [(4, m.id) for m in self.mapped("buffer_ids")]
        return res
