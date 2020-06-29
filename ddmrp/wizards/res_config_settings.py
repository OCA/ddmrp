# Copyright 2020 ForgeFlow S.L. (http://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    module_ddmrp_history = fields.Boolean(
        string="Store historical data from stock buffers",
    )
    ddmrp_auto_update_nfp = fields.Boolean(
        related="company_id.ddmrp_auto_update_nfp", readonly=False
    )
