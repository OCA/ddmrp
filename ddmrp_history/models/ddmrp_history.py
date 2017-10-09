# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models
from openerp.addons import decimal_precision as dp

UNIT = dp.get_precision('Product Unit of Measure')


class DdmrpHistory(models.Model):
    _name = "ddmrp.history"

    orderpoint_id = fields.Many2one(
        comodel_name="stock.warehouse.orderpoint", string="Buffer",
        readonly=True, ondelete='cascade')
    date = fields.Datetime(
        string="Date", readonly=True)
    top_of_red = fields.Float(
        string="TOR", readonly=True, help="Top of Red")
    top_of_yellow = fields.Float(
        string="TOY", readonly=True, help="Top of Yellow")
    top_of_green = fields.Float(
        string="TOG", readonly=True, help="Top of Green")
    net_flow_position = fields.Float(
        string="NFP", digits=UNIT, readonly=True, help="Net flow position")
    on_hand_position = fields.Float(
        string="OHP", digits=UNIT, readonly=True, help="On-Hand Position")
