# -*- coding: utf-8 -*-
# Copyright 2017-18 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from .stock_warehouse_orderpoint import _PRIORITY_LEVEL


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    ddmrp_comment = fields.Text(string="Follow-up Notes")


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    def create(self, vals):
        record = super(PurchaseOrderLine, self).create(vals)
        record._calc_execution_priority()
        return record

    @api.multi
    def _calc_execution_priority(self):
        prods = self.filtered(
            lambda r: r.orderpoint_id and r.state not in ['done', 'cancel'])
        for rec in prods:
            rec.execution_priority_level = \
                rec.orderpoint_id.execution_priority_level
            rec.on_hand_percent = rec.orderpoint_id.on_hand_percent
        (self - prods).write({
            'execution_priority_level': None,
            'on_hand_percent': None,
        })

    orderpoint_id = fields.Many2one(index=True)
    execution_priority_level = fields.Selection(
        string="Buffer On-Hand Status Level",
        selection=_PRIORITY_LEVEL, readonly=True,
    )
    on_hand_percent = fields.Float(
        string="On Hand/TOR (%)", readonly=True,
    )
    ddmrp_comment = fields.Text(related="order_id.ddmrp_comment")
