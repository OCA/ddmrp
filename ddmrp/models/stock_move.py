# Copyright 2019-20 ForgeFlow S.L. (http://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    buffer_ids = fields.Many2many(
        comodel_name="stock.buffer", string="Linked Stock Buffers",
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

    def write(self, vals):
        res = super(StockMove, self).write(vals)
        if "state" in vals and self.env.company.ddmrp_auto_update_nfp:
            self._update_ddmrp_nfp()
        return res

    def _update_ddmrp_nfp(self):
        if self.env.context.get("no_ddmrp_auto_update_nfp"):
            return True
        # Find buffers that can be affected. `out_buffers` will see the move as
        # outgoing and `in_buffers` as incoming.
        out_buffers = in_buffers = self.env["stock.buffer"]
        for move in self:
            out_buffers = move.mapped("product_id.buffer_ids").filtered(
                lambda buffer: (
                    move.location_id.is_sublocation_of(buffer.location_id)
                    and not move.location_dest_id.is_sublocation_of(buffer.location_id)
                )
            )
            in_buffers = move.mapped("product_id.buffer_ids").filtered(
                lambda buffer: (
                    not move.location_id.is_sublocation_of(buffer.location_id)
                    and move.location_dest_id.is_sublocation_of(buffer.location_id)
                )
            )

        for buffer in out_buffers.with_context(no_ddmrp_history=True):
            buffer.cron_actions(only_nfp="out")
        for buffer in in_buffers.with_context(no_ddmrp_history=True):
            buffer.cron_actions(only_nfp="in")
