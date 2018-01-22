# -*- coding: utf-8 -*-
# Copyright 2017-18 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    @api.multi
    @api.depends('move_finished_ids', 'mrp_production_request_id')
    def _compute_orderpoint_id(self):
        from_request = self.filtered(lambda mo: mo.mrp_production_request_id)
        super(MrpProduction, self - from_request)._compute_orderpoint_id()
        for rec in from_request:
            rec.orderpoint_id = rec.mrp_production_request_id.orderpoint_id
