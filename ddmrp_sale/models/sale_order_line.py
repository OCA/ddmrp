# Copyright 2021 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    exclude_from_adu = fields.Boolean(
        string="Exclude from ADU calculation",
        copy=False,
        help="If this flag is set related stock moves will be excluded from "
        "ADU calculation",
    )

    def write(self, vals):
        if "exclude_from_adu" in vals:
            self.mapped("move_ids").write(
                {"exclude_from_adu": vals.get("exclude_from_adu")}
            )
        return super().write(vals)
