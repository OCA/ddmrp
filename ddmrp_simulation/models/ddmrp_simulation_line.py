# Copyright 2020 KMEE
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _


class DdmrpSimulationLine(models.Model):

    _name = 'ddmrp.simulation.line'
    _description = 'Ddmrp_simulation Line'  # TODO

    simulation_id = fields.Many2one(
        comodel_name='ddmrp.simulation',
        required=True,
    )
    product_id = fields.Many2one(
        comodel_name='product.product',
        string='Product',
        required=True,
    )
    date = fields.Date(
        string='Date',
    )
    on_hand = fields.Float(
        string='On hand',
        help='On hand position on that day'
    )
    demand = fields.Float(
        string='Demand',
        help='Demand position on that day'
    )
