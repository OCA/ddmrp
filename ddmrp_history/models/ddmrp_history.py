# Copyright 2017-20 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class DdmrpHistory(models.Model):
    _name = "ddmrp.history"
    _description = "DDMRP History"

    buffer_id = fields.Many2one(
        comodel_name="stock.buffer",
        string="Buffer",
        ondelete="cascade",
        index=True,
    )
    date = fields.Datetime()
    top_of_red = fields.Float(
        string="TOR",
        help="Top of Red",
        group_operator="avg",
    )
    top_of_yellow = fields.Float(
        string="TOY",
        help="Top of Yellow",
        group_operator="avg",
    )
    top_of_green = fields.Float(
        string="TOG",
        help="Top of Green",
        group_operator="avg",
    )
    net_flow_position = fields.Float(
        string="NFP",
        digits="Product Unit of Measure",
        help="Net flow position",
        group_operator="avg",
    )
    on_hand_position = fields.Float(
        string="OHP",
        digits="Product Unit of Measure",
        help="On-Hand Position",
        group_operator="avg",
    )
    adu = fields.Float(
        string="ADU",
        digits="Product Unit of Measure",
        group_operator="avg",
        help="Average Daily Usage",
    )
    company_id = fields.Many2one(
        related="buffer_id.company_id",
    )
