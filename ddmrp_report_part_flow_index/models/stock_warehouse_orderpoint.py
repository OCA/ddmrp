# Copyright 2017-24 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class StockWarehouseOrderpoint(models.Model):
    _inherit = "stock.warehouse.orderpoint"

    flow_index_group_id = fields.Many2one(
        "ddmrp.flow.index.group", string="Flow Index Group"
    )
