# Copyright 2020 KMEE
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _


class DdmrpSimulationProductResult(models.Model):

    _name = 'ddmrp.simulation.product.result'
    _inherit = 'ddmrp.simulation.result.mixin',
    _description = 'Ddmrp Simulation Product Result'  # TODO

    simulation_product_id = fields.Many2one(
        comodel_name='ddmrp.simulation.product',
    )
    simulation_id = fields.Many2one(
        related='simulation_product_id.simulation_id',
    )
    product_id = fields.Many2one(
        comodel_name='product.product',
        related='simulation_product_id.product_id',
        store=True,
    )
