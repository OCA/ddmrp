# Copyright 2019-20 ForgeFlow S.L. (http://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    buffer_ids = fields.Many2many(
        comodel_name="stock.buffer",
        string="Linked Stock Buffers",
    )
    # Add an index as '_find_buffer_link' method is using it as search criteria
    created_purchase_line_id = fields.Many2one(index=True)

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
        if self and self.env.company.ddmrp_auto_update_nfp:
            # Stock moves changes can be triggered by users without
            # access to write stock buffers, thus we do it with sudo.
            if "state" in vals:
                self.sudo()._update_ddmrp_nfp()
            elif "location_id" in vals or "location_dest_id" in vals:
                self.sudo().filtered(
                    lambda m: m.state
                    in ("confirmed", "partially_available", "assigned")
                )._update_ddmrp_nfp()
        return res

    @api.model_create_multi
    def create(self, vals_list):
        moves = super(StockMove, self).create(vals_list)
        # TODO should we use @api.model_create_single instead?
        moves_to_update_ids = []
        for vals, move in zip(vals_list, moves):
            if (
                "state" in vals
                and move.state not in ("draft", "cancel")
                and self.env.company.ddmrp_auto_update_nfp
            ):
                moves_to_update_ids.append(move.id)
        # Stock moves state changes can be triggered by users without
        # access to write stock buffers, thus we do it with sudo.
        if moves_to_update_ids:
            self.browse(moves_to_update_ids).sudo()._update_ddmrp_nfp()
        return moves

    def _find_buffers_to_update_nfp(self):
        # Find buffers that can be affected. `out_buffers` will see the move as
        # outgoing and `in_buffers` as incoming.
        out_buffers = in_buffers = self.env["stock.buffer"]
        for move in self:
            out_buffers |= move.mapped("product_id.buffer_ids").filtered(
                lambda buffer: (
                    move.location_id.is_sublocation_of(buffer.location_id)
                    and not move.location_dest_id.is_sublocation_of(buffer.location_id)
                )
            )
            in_buffers |= move.mapped("product_id.buffer_ids").filtered(
                lambda buffer: (
                    not move.location_id.is_sublocation_of(buffer.location_id)
                    and move.location_dest_id.is_sublocation_of(buffer.location_id)
                )
            )
        return out_buffers, in_buffers

    def _update_ddmrp_nfp(self):
        if self.env.context.get("no_ddmrp_auto_update_nfp"):
            return True
        out_buffers, in_buffers = self._find_buffers_to_update_nfp()
        for buffer in out_buffers.with_context(no_ddmrp_history=True):
            buffer.cron_actions(only_nfp="out")
        for buffer in in_buffers.with_context(no_ddmrp_history=True):
            buffer.cron_actions(only_nfp="in")
