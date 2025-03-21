# Copyright 2017-21 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class DdmrpProductReplace(models.TransientModel):
    _name = "ddmrp.product.replace"
    _description = "DDMRP Product Replace"

    old_product_ids = fields.Many2many(
        comodel_name="product.product",
        string="Replaced Products",
        help="Product to be replaced.",
        required=True,
        ondelete="cascade",
    )
    multi_product = fields.Boolean(compute="_compute_multi_product")
    primary_old_product_id = fields.Many2one(
        string="Primary Replaced Product",
        comodel_name="product.product",
        compute="_compute_primary_old_product_id",
        store=True,
        readonly=False,
        domain="[('id', 'in', old_product_ids)]",
    )
    buffer_ids = fields.Many2many(
        comodel_name="stock.buffer",
        string="Affected Buffers",
        readonly=False,
        compute="_compute_buffer_ids",
        store=True,
    )
    is_already_replaced = fields.Boolean(
        compute="_compute_is_already_replaced",
    )
    new_product_id = fields.Many2one(
        comodel_name="product.product",
        string="Substitute Product",
        help="Product that is going to replace the other one.",
    )
    mode = fields.Selection(
        selection=[
            ("new_buffer", "Create a new buffer for the replacing product."),
            ("use_existing", "Replace product in existing buffers"),
        ],
        default="new_buffer",
        required=True,
    )
    use_existing = fields.Selection(
        string="Use Existing/New Product",
        required=True,
        selection=[("existing", "Use Existing Product"), ("new", "Create New Product")],
    )
    new_product_name = fields.Char()
    new_product_default_code = fields.Char(string="New Product Internal Ref.")
    copy_route = fields.Boolean(string="Copy Routes")
    copy_putaway = fields.Boolean(string="Copy Put Away Strategy")
    copy_packaging = fields.Boolean()
    consider_past_demand = fields.Boolean(
        string="Consider Old Product Demand",
        help="Consider Old product moves as demand for new product",
        default=True,
    )

    @api.depends("old_product_ids")
    def _compute_multi_product(self):
        for rec in self:
            rec.multi_product = len(rec.old_product_ids) > 1

    @api.depends("old_product_ids")
    def _compute_primary_old_product_id(self):
        for rec in self:
            product = fields.first(rec.old_product_ids)
            if isinstance(product.id, models.NewId):
                # NewId instances are not handled correctly in v13, this is a
                # small workaround. In future versions it might not be needed.
                product_id = product.id.origin
                product = self.env["product.product"].browse(product_id)
            rec.primary_old_product_id = product

    @api.depends("old_product_ids")
    def _compute_buffer_ids(self):
        for rec in self:
            rec.buffer_ids = self.env["stock.buffer"].search(
                [("product_id", "in", rec.old_product_ids.ids)]
            )

    @api.depends("buffer_ids")
    def _compute_is_already_replaced(self):
        for rec in self:
            rec.is_already_replaced = any(b.replaced_by_id for b in rec.buffer_ids)

    @api.constrains("buffer_ids")
    def _check_buffer_ids(self):
        for rec in self:
            if rec.old_product_ids and any(
                b.product_id not in rec.old_product_ids for b in rec.buffer_ids
            ):
                raise ValidationError(
                    _(
                        "Some of the affected buffers have a different product than "
                        "the replaced ones."
                    )
                )

    def _do_replacement_use_existing(self):
        vals = {
            "product_id": self.new_product_id.id,
        }
        if self.consider_past_demand:
            vals["demand_product_ids"] = [
                (6, 0, (self.old_product_ids + self.new_product_id).ids)
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

    def _do_replacement_new_buffer(self):
        primary_old = self.primary_old_product_id
        new_buffers = self.env["stock.buffer"]
        for replaced in self.buffer_ids.filtered(lambda b: b.product_id == primary_old):
            default = dict(
                product_id=self.new_product_id.id,
                auto_procure=False,
                demand_product_ids=False,
            )
            replacing = replaced.copy(default=default)
            replaced.write({"replaced_by_id": replacing.id})
            new_buffers |= replacing
        for replaced in self.buffer_ids.filtered(lambda b: b.product_id != primary_old):
            # Do not create buffers for non-primary products.
            # Instead assign one of the already created.
            replacing = fields.first(
                new_buffers.filtered(lambda b: b.location_id == replaced.location_id)  # noqa: B023
            )
            if not replacing:
                replacing = new_buffers[0]
            replaced.write({"replaced_by_id": replacing.id})
        if self.consider_past_demand:
            for buffer in new_buffers:
                recursive_buffers = buffer._recursive_replacement_for_ids(
                    buffer.replacement_for_ids
                )
                buffer.write(
                    {
                        "demand_product_ids": [
                            (
                                6,
                                0,
                                (
                                    recursive_buffers.mapped("product_id")
                                    + buffer.product_id
                                ).ids,
                            )
                        ],
                    }
                )
        new_buffers.cron_actions()
        return {
            "name": _("New Stock Buffers"),
            "domain": [("id", "in", new_buffers.ids)],
            "view_mode": "list,form",
            "res_model": "stock.buffer",
            "type": "ir.actions.act_window",
        }

    def button_validate(self):
        self.ensure_one()
        if self.is_already_replaced:
            raise ValidationError(_("Some of the buffers have already been replaced."))
        if not self.buffer_ids:
            raise ValidationError(_("No affected buffers found."))
        # Only the first product is used as a template to create new products/buffers.
        primary_old = self.primary_old_product_id
        if self.use_existing == "new":
            default = dict(
                name=self.new_product_name,
                default_code=self.new_product_default_code,
            )
            if not self.copy_route:
                default["route_ids"] = None
            self.new_product_id = primary_old.copy(default=default)
        elif self.use_existing == "existing":
            if self.copy_route:
                self.new_product_id.write(
                    {"route_ids": [(6, 0, primary_old.route_ids.ids)]}
                )
        # Check if copy putaway strategies is True
        if self.copy_putaway:
            # Check if there exist putaway strategies for the from product
            putaway_ids = self.env["stock.putaway.rule"].search(
                [("product_id", "=", primary_old.id)]
            )
            if putaway_ids:
                # Copy putaway strategies
                default_putaway = dict(
                    product_id=self.new_product_id.id,
                )
                for pa in putaway_ids:
                    pa.copy(default=default_putaway)
        if self.copy_packaging:
            packs = self.env["product.packaging"].search(
                [("product_id", "=", primary_old.id)]
            )
            if packs:
                default_packs = dict(
                    product_id=self.new_product_id.id,
                )
                for pack in packs:
                    pack.copy(default=default_packs)

        if self.mode == "use_existing":
            res = self._do_replacement_use_existing()
        elif self.mode == "new_buffer":
            res = self._do_replacement_new_buffer()
        return res
