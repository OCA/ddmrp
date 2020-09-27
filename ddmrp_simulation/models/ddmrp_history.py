# Copyright 2020 KMEE
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class DdmrpHistory(models.Model):
    _inherit = "ddmrp.history"

    on_hand_simulation = fields.Float(
        string="OHS",
        digits="Product Unit of Measure",
        help="On-Hand Position of Simulation",
        group_operator="avg",
    )
