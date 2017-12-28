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

    @api.multi
    def _get_procurements_domain(self):
        self.ensure_one()
        return [('purchase_line_id', '=', self.id)]

    @api.model
    def _find_orderpoint_from_procurement(self, procurement):
        procurement = procurement.move_dest_id.procurement_id
        orderpoint = procurement.orderpoint_id
        return procurement, orderpoint

    @api.multi
    @api.depends("product_id")
    def _compute_orderpoint_id(self):
        for rec in self:
            domain = rec._get_procurements_domain()
            procurements = rec.env['procurement.order'].search(domain)
            orderpoints = procurements.mapped('orderpoint_id')
            if orderpoints:
                rec.orderpoint_id = orderpoints[0]
            else:
                for procurement in procurements:
                    orderpoint = False
                    originating_procurement = procurement
                    while not orderpoint:
                        originating_procurement, orderpoint = \
                            self._find_orderpoint_from_procurement(
                                originating_procurement)
                        if orderpoint:
                            rec.orderpoint_id = orderpoint
                        if not originating_procurement:
                            break

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

    orderpoint_id = fields.Many2one(
        comodel_name='stock.warehouse.orderpoint',
        string="Reordering rule",
        compute='_compute_orderpoint_id', store=True, index=True,
    )
    execution_priority_level = fields.Selection(
        string="Buffer On-Hand Status Level",
        selection=_PRIORITY_LEVEL, readonly=True,
    )
    on_hand_percent = fields.Float(
        string="On Hand/TOR (%)", readonly=True,
    )
    ddmrp_comment = fields.Text(related="order_id.ddmrp_comment")
