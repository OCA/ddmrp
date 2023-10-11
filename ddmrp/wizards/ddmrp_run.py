# Copyright 2018-20 ForgeFlow S.L. (http://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import models


class DdmrpRun(models.TransientModel):
    _name = "ddmrp.run"
    _description = "DDMRP Manual Run Wizard"

    def run_cron_ddmrp_adu(self):
        self.env["stock.buffer"].cron_ddmrp_adu(True)

    def run_cron_ddmrp(self):
        self.env["stock.buffer"].cron_ddmrp(True)
