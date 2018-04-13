# Copyright 2016-18 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, models, _
from odoo.exceptions import Warning as UserError


class StockSchedulerCompute(models.TransientModel):
    _inherit = 'stock.scheduler.compute'

    @api.multi
    def procure_calculation(self):
        """Override standard method to disable the feature."""
        raise UserError(_('The option to compute minimum stock rules '
                          'automatically has been disabled.'))
