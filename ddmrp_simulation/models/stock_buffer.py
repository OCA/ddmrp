# Copyright 2020 KMEE
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockBuffer(models.Model):

    _inherit = 'stock.buffer'

    simulation_id = fields.Many2one(
        comodel_name='ddmrp.simulation',
        readonly=True
    )
