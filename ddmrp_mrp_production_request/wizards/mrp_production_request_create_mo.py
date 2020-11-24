# Copyright 2018 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class MrpProductionRequestCreateMo(models.TransientModel):
    _inherit = "mrp.production.request.create.mo"

    @api.multi
    def _prepare_manufacturing_order(self):
        res = super(
            MrpProductionRequestCreateMo, self)._prepare_manufacturing_order()
        request_id = self.mrp_production_request_id
        if request_id.orderpoint_id:
            res['orderpoint_id'] = request_id.orderpoint_id.id
            res['execution_priority_level'] = \
                request_id.orderpoint_id.execution_priority_level
            res['on_hand_percent'] = \
                request_id.orderpoint_id.on_hand_percent
        return res
