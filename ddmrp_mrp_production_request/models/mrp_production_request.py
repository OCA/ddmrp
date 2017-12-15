# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models

_PRIORITY_LEVEL = [
    ('1_red', 'Red'),
    ('2_yellow', 'Yellow'),
    ('3_green', 'Green')
]


class MrpProductionRequest(models.Model):
    _inherit = "mrp.production.request"

    def _search_orderpoints(self):
        self.ensure_one()
        return [('name', '=', self.move_prod_id.origin)]

    @api.model
    def _find_orderpoint_from_procurement(self, procurement):
        orderpoint = procurement.move_dest_id.procurement_id.orderpoint_id
        procurement = procurement.move_dest_id.procurement_id
        return procurement, orderpoint

    @api.multi
    @api.depends('procurement_id')
    def _compute_orderpoint_id(self):
        for rec in self:
            orderpoint = rec.procurement_id.orderpoint_id
            if orderpoint:
                rec.orderpoint_id = orderpoint
            else:
                orderpoint = False
                originating_procurement = rec.procurement_id
                while not orderpoint:
                    originating_procurement, orderpoint = \
                        self._find_orderpoint_from_procurement(
                            originating_procurement)
                    if orderpoint:
                        rec.orderpoint_id = orderpoint
                    if not originating_procurement:
                        break

    @api.multi
    @api.depends("orderpoint_id")
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

    def _search_execution_priority(self, operator, value):  # TODO: to remove
        """Search on the execution priority by evaluating on all
        open manufacturing orders."""
        all_records = self.search([('state', 'not in', ['done', 'cancel'])])
        if operator == '=':
            found_ids = [a.id for a in all_records
                         if a.execution_priority_level == value]
        elif operator == 'in' and isinstance(value, list):
            found_ids = [a.id for a in all_records
                         if a.execution_priority_level in value]
        elif operator in ("!=", "<>"):
            found_ids = [a.id for a in all_records
                         if a.execution_priority_level != value]
        elif operator == 'not in' and isinstance(value, list):
            found_ids = [a.id for a in all_records
                         if a.execution_priority_level not in value]
        else:
            raise NotImplementedError(
                'Search operator %s not implemented for value %s'
                % (operator, value)
            )
        return [('id', 'in', found_ids)]

    orderpoint_id = fields.Many2one(
        comodel_name='stock.warehouse.orderpoint', store=True, index=True,
        string="Reordering rule", compute='_compute_orderpoint_id')
    execution_priority_level = fields.Selection(
        string="Buffer On-Hand Alert Level", selection=_PRIORITY_LEVEL,
        readonly=True,
    )
    on_hand_percent = fields.Float(
        string="On Hand/TOR (%)", compute="_calc_execution_priority",
        store=True) # TODO: remove compute and store.
