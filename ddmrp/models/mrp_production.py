# -*- coding: utf-8 -*-
# © 2016 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# © 2016 Aleph Objects, Inc. (https://www.alephobjects.com/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models
from .stock_warehouse_orderpoint import _PRIORITY_LEVEL


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    @api.model
    def _search_procurements(self):
        return [('production_id', '=', self.id)]

    @api.model
    def _search_orderpoints(self):
        return [('name', '=', self.move_prod_id.origin)]

    @api.multi
    @api.depends('move_prod_id')
    def _compute_orderpoint_id(self):
        for rec in self:
            domain = rec._search_procurements()
            procurements = rec.env['procurement.order'].search(domain)
            orderpoints = [procurement.orderpoint_id for procurement in
                           procurements if procurement.orderpoint_id]
            if orderpoints:
                rec.orderpoint_id = orderpoints[0]
            else:
                domain = rec._search_orderpoints()
                orderpoints = rec.env['stock.warehouse.orderpoint'].search(
                    domain)
                if orderpoints:
                    rec.orderpoint_id = orderpoints[0]

    @api.multi
    @api.depends("orderpoint_id")
    def _compute_execution_priority(self):
        for rec in self:
            if rec.state not in ['done', 'cancel']:
                rec.execution_priority_level = \
                    rec.orderpoint_id.execution_priority_level
                rec.on_hand_percent = rec.orderpoint_id.on_hand_percent

    def _search_execution_priority(self, operator, value):
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
        comodel_name='stock.warehouse.orderpoint',
        string="Reordering rule", compute='_compute_orderpoint_id')
    execution_priority_level = fields.Selection(
        string="Buffer On-Hand Alert Level",
        selection=_PRIORITY_LEVEL,
        compute="_compute_execution_priority",
        search="_search_execution_priority")
    on_hand_percent = fields.Float(string="On Hand/TOG (%)",
                                   compute="_compute_execution_priority")
