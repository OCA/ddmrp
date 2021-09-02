# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)


from odoo import api, fields, models


class MakeProcurementBufferItem(models.TransientModel):
    _inherit = "make.procurement.buffer.item"

    packaging_id = fields.Many2one(string="Package", comodel_name="product.packaging",)
    packaging_qty = fields.Integer(string="Package Qty")

    @api.onchange("packaging_qty", "packaging_id")
    def onchange_packaging(self):
        if not self.packaging_id:
            self.packaging_qty = False
            return
        if not self.packaging_qty:
            self.packaging_qty = 1
        self.qty = self.packaging_id.qty * self.packaging_qty
