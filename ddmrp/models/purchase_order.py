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
        comodel_name="stock.buffer", string="Stock Buffers", copy=False, readonly=True,
    )
    execution_priority_level = fields.Selection(
        string="Buffer On-Hand Status Level", selection=_PRIORITY_LEVEL, readonly=True,
    )
    on_hand_percent = fields.Float(string="On Hand/TOR (%)", readonly=True,)
    ddmrp_comment = fields.Text(related="order_id.ddmrp_comment")

    def create(self, vals):
        record = super(PurchaseOrderLine, self).create(vals)
        record._calc_execution_priority()
        return record

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
