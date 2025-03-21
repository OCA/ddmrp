# Copyright 2019-21 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class StockBuffer(models.Model):
    _inherit = "stock.buffer"

    replaced_by_id = fields.Many2one(
        comodel_name="stock.buffer",
        string="Replaced by",
        help="The product in this buffer is replaced by the product of selected "
        "buffer. When you replace another buffer:\n - Past Demand of the "
        "replacement buffer will include the past demand of this product\n"
        " - Several buffers can be replaced in chained and coexist at the "
        "same time: A replaces B that replaces C, then A aggregates both B"
        " and C where B only aggregates C",
        tracking=True,
    )
    replaced_by_alert_text = fields.Char(
        compute="_compute_replaced_by_alert_text",
    )
    replacement_for_ids = fields.One2many(
        string="Replaces",
        comodel_name="stock.buffer",
        inverse_name="replaced_by_id",
    )
    replacement_for_count = fields.Integer(
        compute="_compute_replacement_for_count",
    )
    is_replacement_product = fields.Boolean(
        string="Replacement Product",
        compute="_compute_is_replacement_product",
        store=True,
        help="The product of this buffer is replacing another product",
    )
    demand_product_ids = fields.Many2many(
        comodel_name="product.product",
        string="Considered As Demand",
        help="This field is used for a correct product replacement within a "
        "DDMRP buffer.",
        copy=False,
    )
    use_replacement_for_buffer_status = fields.Boolean(
        string="Include Incoming & On-Hands of replaced products",
        compute="_compute_use_replacement_for_buffer_status",
        store=True,
        readonly=False,
        copy=False,
        help="If you tick this option, the buffer will consider the incoming "
        "and on-hand of all products it replaces and this will impact its "
        "NFP.",
    )

    @api.constrains("replaced_by_id")
    def _check_replaced_by_id(self):
        if self._has_cycle(field_name="replaced_by_id"):
            raise ValidationError(
                _('You cannot create recursive "Replaced by" chains.')
            )

    @api.constrains("demand_product_ids")
    def _check_demand_product_ids(self):
        for rec in self:
            if rec.demand_product_ids and rec.product_id not in rec.demand_product_ids:
                raise ValidationError(
                    _("Buffered product must be considered as demand.")
                )

    def _compute_replaced_by_alert_text(self):
        for rec in self:
            if rec.replaced_by_id:
                rec.replaced_by_alert_text = (
                    _("This product is replaced by %s.")
                    % rec.replaced_by_id.product_id.display_name
                )
            else:
                rec.replaced_by_alert_text = ""

    def _compute_replacement_for_count(self):
        for rec in self:
            rec.replacement_for_count = len(rec.replacement_for_ids)

    @api.depends("replaced_by_id", "replacement_for_ids", "replacement_for_ids.active")
    def _compute_is_replacement_product(self):
        for rec in self:
            rec.is_replacement_product = (
                rec.replacement_for_ids and not rec.replaced_by_id
            )

    @api.depends("item_type")
    def _compute_use_replacement_for_buffer_status(self):
        for rec in self:
            rec.use_replacement_for_buffer_status = rec.item_type in [
                "manufactured",
                "purchased",
            ]

    @api.depends("item_type")
    def _compute_procure_recommended_qty(self):
        replaced = self.filtered(
            lambda r: r.replaced_by_id and r.item_type in ["manufactured", "purchased"]
        )
        res = super(StockBuffer, self - replaced)._compute_procure_recommended_qty()
        for rec in replaced:
            rec.procure_recommended_qty = 0.0
        return res

    def _past_moves_domain(self, date_from, date_to, locations):
        if not self.demand_product_ids:
            return super()._past_moves_domain(date_from, date_to, locations)
        domain = super()._past_moves_domain(date_from, date_to, locations)
        index_replace = False
        for n, clause in enumerate(domain):
            if isinstance(clause, tuple) and clause[0] == "product_id":
                index_replace = n
        if isinstance(index_replace, int):
            domain[index_replace] = ("product_id", "in", self.demand_product_ids.ids)
        return domain

    @api.model
    def _recursive_replacement_for_ids(self, buffers):
        """Returns the list of buffers being replaced recursively."""
        res = self.env["stock.buffer"]
        for rec in buffers:
            if rec.replacement_for_ids:
                res += self._recursive_replacement_for_ids(rec.replacement_for_ids)
            res += rec
        return res

    def _calc_product_available_qty(self):
        res = super()._calc_product_available_qty()
        for rec in self:
            if not (rec.use_replacement_for_buffer_status and rec.replacement_for_ids):
                continue
            for buffer in rec.replacement_for_ids:
                # Update 'incoming_total_qty'
                replacements_incoming_qty = buffer.product_uom._compute_quantity(
                    buffer.incoming_total_qty,
                    rec.product_uom,
                    round=False,
                )
                rec.incoming_total_qty += replacements_incoming_qty
                # Update 'product_location_qty_available_not_res'
                replacements_qty_not_res = buffer.product_uom._compute_quantity(
                    buffer.product_location_qty_available_not_res,
                    rec.product_uom,
                    round=False,
                )
                rec.product_location_qty_available_not_res += replacements_qty_not_res
        return res

    def _search_stock_moves_incoming_domain(self, outside_dlt=False):
        domain = super()._search_stock_moves_incoming_domain(outside_dlt=outside_dlt)
        if not (self.use_replacement_for_buffer_status and self.replacement_for_ids):
            return domain
        index_replace = False
        for n, clause in enumerate(domain):
            if isinstance(clause, tuple) and clause[0] == "product_id":
                index_replace = n
        if isinstance(index_replace, int):
            domain[index_replace] = (
                "product_id",
                "in",
                (self + self._recursive_replacement_for_ids(self.replacement_for_ids))
                .mapped("product_id")
                .ids,
            )
        return domain

    def _search_stock_moves_qualified_demand_domain(self):
        domain = super()._search_stock_moves_qualified_demand_domain()
        if not self.demand_product_ids:
            return domain
        domain = [x for x in domain if x[0] != "product_id"] + [
            ("product_id", "in", self.demand_product_ids.ids)
        ]
        return domain

    def action_view_buffers_replaced(self):
        result = self.env["ir.actions.actions"]._for_xml_id("ddmrp.action_stock_buffer")
        result["name"] = _("Buffers Replaced")
        result["domain"] = [("id", "in", self.replacement_for_ids.ids)]
        return result
