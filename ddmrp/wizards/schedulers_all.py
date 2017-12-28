# -*- coding: utf-8 -*-
# Copyright 2016-18 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, models, _
from odoo.exceptions import Warning as UserError


class ProcurementComputeAll(models.TransientModel):
    _inherit = 'procurement.order.compute.all'

    @api.multi
    def procure_calculation(self):
        """Override standard method to disable the feature."""
        raise UserError(_('The option to compute minumum stock rules '
                          'automatically has been disabled.'))
