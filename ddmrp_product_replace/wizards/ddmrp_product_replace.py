# Copyright 2017-21 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import _, api, fields, models


class DdmrpProductReplace(models.TransientModel):
    _name = "ddmrp.product.replace"
    _description = "DDMRP Product Replace"

    @api.depends("old_product_id")
    def _compute_buffer_ids(self):
        for rec in self:
            rec.buffer_ids = self.env["stock.buffer"].search(
                [("product_id", "=", rec.old_product_id.id)]
            )

    old_product_id = fields.Many2one(
        comodel_name="product.product",
        string="Replaced Product",
        help="Product to be replaced.",
        required=True,
        ondelete="cascade",
    )
    buffer_ids = fields.Many2many(
        comodel_name="stock.buffer",
        string="Affected Buffers",
        readonly=True,
        compute="_compute_buffer_ids",
    )
    new_product_id = fields.Many2one(
        comodel_name="product.product",
        string="Substitute Product",
        help="Product that is going to replace the other one.",
    )
    use_existing = fields.Selection(
        string="Use Existing/New Product",
        required=True,
        selection=[("existing", "Use Existing Product"), ("new", "Create New Product")],
    )
    new_product_name = fields.Char(string="New Product Name")
    new_product_default_code = fields.Char(string="New Product Internal Ref.")
    copy_route = fields.Boolean(string="Copy Routes")
    copy_putaway = fields.Boolean(string="Copy Put Away Strategy")
    consider_past_demand = fields.Boolean(
        string="Consider Old Product Demand",
        help="Consider Old product moves as demand for new product",
        default=True,
    )

    def button_validate(self):
        self.ensure_one()
        if self.use_existing == "new":
            default = dict(
                name=self.new_product_name, default_code=self.new_product_default_code,
            )
            if not self.copy_route:
                default["route_ids"] = None
            self.new_product_id = self.old_product_id.copy(default=default)
        elif self.use_existing == "existing":
            if self.copy_route:
                self.new_product_id.write(
                    {"route_ids": [(6, 0, self.old_product_id.route_ids.ids)]}
                )
        # Check if copy putaway strategies is True
        if self.copy_putaway:
            # Check if there exist putaway strategies for the from product
            putaway_ids = self.env["stock.putaway.rule"].search(
                [("product_id", "=", self.old_product_id.id)]
            )
            if putaway_ids:
                # Copy putaway strategies
                default_putaway = dict(product_id=self.new_product_id.id,)
                putaway_ids.copy(default=default_putaway)
        if self.buffer_ids:
            vals = {
                "product_id": self.new_product_id.id,
            }
            if self.consider_past_demand:
                vals["demand_product_ids"] = [
                    (6, 0, (self.old_product_id + self.new_product_id).ids)
                ]
            self.buffer_ids.write(vals)
        return {
            "name": _("Replacing Product"),
            "res_id": self.new_product_id.id,
            "view_type": "form",
            "view_mode": "form",
            "res_model": "product.product",
            "type": "ir.actions.act_window",
        }
