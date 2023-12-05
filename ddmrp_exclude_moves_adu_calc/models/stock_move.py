# Copyright 2017-21 ForgeFlow (http://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import _, fields, models
from odoo.exceptions import UserError


class StockMove(models.Model):
    _inherit = "stock.move"

    exclude_from_adu = fields.Boolean(
        string="Exclude this move from ADU calculation",
        copy=False,
        help="If this flag is set this stock move will be excluded from ADU "
        "calculation",
        index=True,
    )

    def _toggle_exclude_from_adu(self):
        if not self.env.user.has_group("stock.group_stock_manager"):
            raise UserError(
                _("Only inventory managers are allowed perform this action.")
            )
        for rec in self:
            rec.exclude_from_adu = not rec.exclude_from_adu
