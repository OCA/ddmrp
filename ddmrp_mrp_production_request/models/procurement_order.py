# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp import api, models


class ProcurementOrder(models.Model):
    _inherit = 'procurement.order'

    @api.multi
    def write(self, vals):
        """Needed to calculate the execution priority of MOs originated from
        a DDMRP buffer just after the creation."""
        res = super(ProcurementOrder, self).write(vals)
        mr_id = vals.get('mrp_production_request_id')
        if mr_id:
            self.env['mrp.production.request'].browse(
                mr_id)._calc_execution_priority()
        return res