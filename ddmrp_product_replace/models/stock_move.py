# Copyright 2021 ForgeFlow S.L. (http://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _find_buffers_to_update_nfp(self):
        out_buffers, in_buffers = super()._find_buffers_to_update_nfp()
        new_out_buffers = out_buffers
        while new_out_buffers:
            new_out_buffers = new_out_buffers.mapped("replaced_by_id")
            out_buffers |= new_out_buffers

        new_in_buffers = in_buffers
        while new_in_buffers:
            new_in_buffers = new_in_buffers.mapped("replaced_by_id")
            in_buffers |= new_in_buffers

        return out_buffers, in_buffers
