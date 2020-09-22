# Copyright 2020 KMEE
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.addons.ddmrp.models.stock_buffer_profile import (
    _ITEM_TYPES,
    _REPLENISH_METHODS,
)


class DdmrpSimulationProduct(models.Model):

    _name = 'ddmrp.simulation.product'
    _description = 'Ddmrp Simulation Product'

    simulation_id = fields.Many2one(
        comodel_name='ddmrp.simulation',
        required=True,
    )
    product_tmpl_id = fields.Many2one(
        comodel_name='product.template',
        related='product_id.product_tmpl_id'
    )
    product_id = fields.Many2one(
        comodel_name='product.product',
    )
    reference = fields.Char(
        related='product_id.default_code',
        store=True,
        readonly=False,
    )
    name = fields.Char(
        related='product_id.name',
        store=True,
        readonly=False,
    )
    standard_price = fields.Float(
        related='product_id.standard_price',
        store=True,
        readonly=False,
    )
    seller_id = fields.Many2one(
        comodel_name='product.supplierinfo',
    )
    lead_time = fields.Integer(
        related='seller_id.delay',
        store=True,
        readonly=False,
    )
    replenish_method = fields.Selection(
        string="Replenishment method",
        selection=_REPLENISH_METHODS,
        default='replenish',
        required=True,
    )
    item_type = fields.Selection(
        string="Item Type",
        selection=_ITEM_TYPES,
        default='purchased',
        required=True,
    )
    lead_time_id = fields.Many2one(
        comodel_name="stock.buffer.profile.lead.time",
        string="Lead Time Factor",
    )
    variability_id = fields.Many2one(
        comodel_name='stock.buffer.profile.variability',
    )
    adu_calculation_method = fields.Many2one(
        comodel_name="product.adu.calculation.method",
        string="ADU calculation method",
        required=True,
        default=lambda self: self.env.ref('ddmrp.adu_calculation_method_fixed')
    )
    stock_buffer_id = fields.Many2one(
        comodel_name='stock.buffer',
    )
