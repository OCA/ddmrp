# Copyright 2018 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class DdmrpRun(models.TransientModel):
    _name = 'ddmrp.run'

    @api.multi
    def run_cron_ddmrp_adu(self):
        self.env['stock.warehouse.orderpoint'].cron_ddmrp_adu(True)

    @api.multi
    def run_cron_ddmrp(self):
        self.env['stock.warehouse.orderpoint'].cron_ddmrp(True)
