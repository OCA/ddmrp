# Copyright 2020 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class Buffer(models.Model):
    _name = "stock.buffer"
    _inherit = ["stock.buffer", "mail.thread", "mail.activity.mixin"]

    buffer_profile_id = fields.Many2one(tracking=True)
    adu_calculation_method = fields.Many2one(tracking=True)
    product_id = fields.Many2one(tracking=True)
    location_id = fields.Many2one(tracking=True)
    warehouse_id = fields.Many2one(tracking=True)
    procure_uom_id = fields.Many2one(tracking=True)
    minimum_order_quantity = fields.Float(tracking=True)
    order_cycle = fields.Float(tracking=True)
    order_spike_horizon = fields.Float(tracking=True)
    procure_min_qty = fields.Float(tracking=True)
    procure_max_qty = fields.Float(tracking=True)
    qty_multiple = fields.Float(tracking=True)
    auto_procure = fields.Boolean(tracking=True)
    auto_procure_option = fields.Selection(tracking=True)
