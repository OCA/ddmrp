# Copyright 2016-20 ForgeFlow S.L. (http://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class MrpMove(models.Model):
    _inherit = "mrp.move"

    # TODO: remove this?
    mrp_qty_to_procure = fields.Float(
        string="Quantity to release", compute="_compute_mrp_qty_release"
    )

    def _compute_mrp_qty_release(self):
        for move in self:
            move.mrp_qty_to_release = move.mrp_qty - sum(
                move.planned_order_up_ids.mapped("qty_released")
            )
