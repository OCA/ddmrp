# Copyright 2017-20 ForgeFlow S.L. (http://www.forgeflow.com)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models

from .stock_buffer import _PRIORITY_LEVEL


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    ddmrp_comment = fields.Text(string="Follow-up Notes")


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    buffer_ids = fields.Many2many(
        comodel_name="stock.buffer",
        string="Stock Buffers",
        copy=False,
        readonly=True,
    )
    execution_priority_level = fields.Selection(
        string="Buffer On-Hand Status Level",
        selection=_PRIORITY_LEVEL,
        readonly=True,
    )
    on_hand_percent = fields.Float(
        string="On Hand/TOR (%)",
        readonly=True,
    )
    ddmrp_comment = fields.Text(related="order_id.ddmrp_comment", readonly=False)

    def create(self, vals):
        record = super().create(vals)
        if record.product_id:
            record._find_buffer_link()
        record._calc_execution_priority()
        return record

    def write(self, vals):
        res = super().write(vals)
        for rec in self:
            if rec.product_id:
                rec._find_buffer_link()
        return res

    def _product_id_change(self):
        res = super()._product_id_change()
        if self.product_id:
            self._find_buffer_link()
        return res

    def _calc_execution_priority(self):
        # TODO: handle serveral buffers? worst scenario, average?
        to_compute = self.filtered(
            lambda r: r.buffer_ids and r.state not in ["done", "cancel"]
        )
        for rec in to_compute:
            rec.execution_priority_level = rec.buffer_ids[0].execution_priority_level
            rec.on_hand_percent = rec.buffer_ids[0].on_hand_percent
        (self - to_compute).write(
            {"execution_priority_level": None, "on_hand_percent": None}
        )

    def _get_domain_buffer_link(self):
        self.ensure_one()
        if not self.product_id:
            # Return impossible domain -> no buffer.
            return [(0, "=", 1)]
        return [
            ("product_id", "=", self.product_id.id),
            ("company_id", "=", self.order_id.company_id.id),
            ("buffer_profile_id.item_type", "=", "purchased"),
            ("warehouse_id", "=", self.order_id.picking_type_id.warehouse_id.id),
        ]

    def _ddmrp_is_mto(self):
        """Return True when this purchase line was raised to satisfy a
        make-to-order demand move.

        ``move_dest_ids`` is the inverse of ``stock.move.created_purchase_line_ids``
        (same relation), so this mirrors ``stock.move._ddmrp_is_mto`` on the
        demand side. Keeping the criterion identical on both sides guarantees
        that a pegged demand move and the purchase line it created are kept out
        of the MTS buffer together, so the net flow position stays consistent.
        """
        self.ensure_one()
        return bool(self.move_dest_ids)

    def _find_buffer_link(self):
        buffer_model = self.env["stock.buffer"]
        for rec in self.filtered(lambda r: not r.buffer_ids):
            if rec._ddmrp_is_mto():
                # MTO lines are not accounted in MTS stock buffers.
                continue
            domain = rec._get_domain_buffer_link()
            buffer = buffer_model.search(domain, limit=1)
            if buffer:
                rec.buffer_ids = buffer
                rec._calc_execution_priority()

    def _prepare_purchase_order_line_from_procurement(
        self,
        product_id,
        product_qty,
        product_uom,
        location_dest_id,
        name,
        origin,
        company_id,
        values,
        po,
    ):
        vals = super()._prepare_purchase_order_line_from_procurement(
            product_id,
            product_qty,
            product_uom,
            location_dest_id,
            name,
            origin,
            company_id,
            values,
            po,
        )
        # If the procurement was run directly by a reordering rule.
        if "buffer_id" in values:
            vals["buffer_ids"] = [(4, values["buffer_id"].id)]
        # If the procurement was run by a stock move.
        elif "buffer_ids" in values:
            vals["buffer_ids"] = [(4, o.id) for o in values["buffer_ids"]]
        return vals
