# Copyright 2024 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    exclude_from_adu = fields.Boolean(
        string="Exclude from ADU calculation",
        compute="_compute_exclude_from_adu",
        inverse="_inverse_exclude_from_adu",
        copy=False,
        help="If this flag is set related stock moves will be excluded from "
        "ADU calculation",
    )

    def _compute_exclude_from_adu(self):
        for rec in self:
            rec.exclude_from_adu = all(move.exclude_from_adu for move in rec.move_ids)

    def _inverse_exclude_from_adu(self):
        for rec in self:
            if rec.exclude_from_adu:
                rec.move_ids.write({"exclude_from_adu": True})
            else:
                rec.move_ids.write({"exclude_from_adu": False})
