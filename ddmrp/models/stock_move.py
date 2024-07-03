# Copyright 2019-20 ForgeFlow S.L. (http://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import _, api, fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    buffer_ids = fields.Many2many(
        comodel_name="stock.buffer",
        string="Linked Stock Buffers",
    )

    def _prepare_procurement_values(self):
        res = super()._prepare_procurement_values()
        if self.buffer_ids:
            res["buffer_ids"] = self.buffer_ids
        return res

    def _merge_moves_fields(self):
        res = super()._merge_moves_fields()
        res["buffer_ids"] = [(4, m.id) for m in self.mapped("buffer_ids")]
        return res

    def write(self, vals):
        res = super().write(vals)
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
        moves = super().create(vals_list)
        # TODO should we use @api.model_create_single instead?
        moves_to_update_ids = []
        for vals, move in zip(vals_list, moves, strict=False):
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
                    move.location_id.is_sublocation_of(buffer.location_id)  # noqa: B023
                    and not move.location_dest_id.is_sublocation_of(buffer.location_id)  # noqa: B023
                )
            )
            in_buffers |= move.mapped("product_id.buffer_ids").filtered(
                lambda buffer: (
                    not move.location_id.is_sublocation_of(buffer.location_id)  # noqa: B023
                    and move.location_dest_id.is_sublocation_of(buffer.location_id)  # noqa: B023
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

    def _get_all_linked_moves(self):
        """Retrieve all linked moves both origin and destination recursively."""

        def get_moves(move_set, attr):
            new_moves = move_set.mapped(attr)
            while new_moves:
                move_set |= new_moves
                new_moves = new_moves.mapped(attr)
            return move_set

        all_moves = (
            self | get_moves(self, "move_orig_ids") | get_moves(self, "move_dest_ids")
        )
        return all_moves

    def _get_source_field_candidates(self):
        """Extend for more source field candidates."""
        return [
            "sale_line_id.order_id",
            "purchase_line_id.order_id",
            "production_id",
            "raw_material_production_id",
            "unbuild_id",
            "repair_id",
            "rma_line_id",
            "picking_id",
        ]

    def _has_nested_field(self, field):
        """Check if an object has a nested chain of fields."""
        current_object = self
        try:
            for f in field.split("."):
                current_object = getattr(current_object, f)
            return True
        except AttributeError:
            return False

    def _get_source_record(self):
        """Find the first source record in the field candidates linked with the moves,
        prioritizing the order of field candidates."""
        moves = self._get_all_linked_moves()
        field_candidates = self._get_source_field_candidates()
        # Iterate over the prioritized list of candidate fields
        for field in field_candidates:
            if self._has_nested_field(field):
                for move in moves:
                    record = move.mapped(field)
                    if record:
                        return record
        return False

    def action_open_stock_move_source(self):
        """Open the source record of the stock move, if it exists."""
        self.ensure_one()
        record = self._get_source_record()
        if record:
            return {
                "name": getattr(record, "name", _("Stock Move Source")),
                "view_mode": "form",
                "res_model": record._name,
                "type": "ir.actions.act_window",
                "res_id": record.id,
            }
        return False
