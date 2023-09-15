# Copyright 2021 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class DdmrpWarningItem(models.Model):
    _name = "ddmrp.warning.item"
    _description = "DDMRP Warning Item"
    _order = "severity desc, id"

    warning_definition_id = fields.Many2one(
        comodel_name="ddmrp.warning.definition",
    )
    buffer_id = fields.Many2one(comodel_name="stock.buffer", ondelete="cascade")
    name = fields.Char(
        compute="_compute_name",
    )
    product_id = fields.Many2one(related="buffer_id.product_id")
    location_id = fields.Many2one(
        related="buffer_id.location_id", groups="stock.group_stock_multi_locations"
    )
    severity = fields.Selection(
        related="warning_definition_id.severity",
        store=True,
        readonly=True,
    )
    company_id = fields.Many2one(
        related="buffer_id.company_id",
        store=True,
    )

    def _compute_name(self):
        for rec in self:
            rec.name = "{} in {}".format(
                rec.warning_definition_id.display_name,
                rec.buffer_id.display_name,
            )
