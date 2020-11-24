# Copyright 2017-18 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.addons.ddmrp.models.stock_warehouse_orderpoint import _PRIORITY_LEVEL


class MrpProductionRequest(models.Model):
    _inherit = "mrp.production.request"

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

    execution_priority_level = fields.Selection(
        string="Buffer On-Hand Alert Level",
        selection=_PRIORITY_LEVEL,
        readonly=True,
    )
    on_hand_percent = fields.Float(
        string="On Hand/TOR (%)",
    )
