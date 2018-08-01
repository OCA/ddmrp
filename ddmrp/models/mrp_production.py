# Copyright 2016-18 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# Copyright 2016 Aleph Objects, Inc. (https://www.alephobjects.com/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models
from .stock_warehouse_orderpoint import _PRIORITY_LEVEL


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    orderpoint_id = fields.Many2one(
        comodel_name='stock.warehouse.orderpoint',
        index=True,
        string="Reordering rule"
    )
    execution_priority_level = fields.Selection(
        string="Buffer On-Hand Alert Level",
        selection=_PRIORITY_LEVEL, readonly=True,
    )
    on_hand_percent = fields.Float(
        string="On Hand/TOR (%)",
    )

    # TODO: remove after PR https://github.com/odoo/odoo/pull/25424 has
    # been merged
    def _generate_finished_moves(self):
        move = super(MrpProduction, self)._generate_finished_moves()
        move.write({
            'date': self.date_planned_finished,
            'date_expected': self.date_planned_finished,
        })

    @api.model
    def create(self, vals):
        record = super(MrpProduction, self).create(vals)
        record._calc_execution_priority()
        return record

    @api.multi
    def _calc_execution_priority(self):
        """Technical note: this method cannot be decorated with api.depends,
        otherwise it would generate a infinite recursion."""
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
