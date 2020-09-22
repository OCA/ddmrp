# Copyright 2020 KMEE
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductProduct(models.Model):

    _inherit = 'product.product'

    simulation_id = fields.Many2one(
        comodel_name='ddmrp.simulation',
        readonly=True
    )
    simulation_product_external_id = fields.Integer(readonly=True, index=True)
