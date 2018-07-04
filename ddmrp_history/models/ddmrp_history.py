# Copyright 2017 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models
from odoo.addons import decimal_precision as dp

UNIT = dp.get_precision("Product Unit of Measure")


class DdmrpHistory(models.Model):
    _name = "ddmrp.history"

    orderpoint_id = fields.Many2one(
        comodel_name="stock.warehouse.orderpoint", string="Buffer",
        readonly=True, ondelete="cascade",
    )
    date = fields.Datetime(
        string="Date", readonly=True,
    )
    top_of_red = fields.Float(
        string="TOR", readonly=True,
        help="Top of Red", group_operator="avg",
    )
    top_of_yellow = fields.Float(
        string="TOY", readonly=True,
        help="Top of Yellow", group_operator="avg",
    )
    top_of_green = fields.Float(
        string="TOG", readonly=True,
        help="Top of Green", group_operator="avg",
    )
    net_flow_position = fields.Float(
        string="NFP", digits=UNIT,
        readonly=True, help="Net flow position",
        group_operator="avg",
    )
    on_hand_position = fields.Float(
        string="OHP", digits=UNIT,
        readonly=True, help="On-Hand Position",
        group_operator="avg",
    )
