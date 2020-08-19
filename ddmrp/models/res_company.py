# Copyright 2020 ForgeFlow S.L. (http://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).


from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    ddmrp_auto_update_nfp = fields.Boolean(
        string="Update NFP on Stock Buffers on relevant events.",
        help="Transfer status changes can trigger the update of relevant "
        "buffer's NFP.",
    )
