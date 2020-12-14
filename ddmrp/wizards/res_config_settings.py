# Copyright 2020 ForgeFlow S.L. (http://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    module_ddmrp_history = fields.Boolean(
        string="Store historical data from stock buffers",
    )
    module_ddmrp_adjustment = fields.Boolean(
        string="apply adjustments to dynamically alter buffers",
    )
    module_ddmrp_coverage_days = fields.Boolean(
        string="Shows the current on-hand for stock buffers expressed "
        "as coverage days.",
    )
    module_ddmrp_packaging = fields.Boolean(string="Use packagings on stock buffers.",)
    module_stock_buffer_capacity_limit = fields.Boolean(
        string="Storage Capacity Limits",
    )
    module_ddmrp_chatter = fields.Boolean(string="Chatter in Stock Buffers",)
    ddmrp_auto_update_nfp = fields.Boolean(
        related="company_id.ddmrp_auto_update_nfp", readonly=False
    )
    ddmrp_adu_calc_include_scrap = fields.Boolean(
        related="company_id.ddmrp_adu_calc_include_scrap", readonly=False
    )
