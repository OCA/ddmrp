# Copyright 2017-24 ForgeFlow S.L. (http://www.forgeflow.com)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import logging

from odoo import _, api, fields, models

_logger = logging.getLogger(__name__)


class MrpBom(models.Model):
    _inherit = "mrp.bom"

    is_buffered = fields.Boolean(
        string="Buffered?",
        compute="_compute_is_buffered",
        help="True when the product has an DDMRP buffer associated.",
    )
    buffer_id = fields.Many2one(
        comodel_name="stock.buffer",
        string="Stock Buffer",
        compute="_compute_buffer",
    )
    dlt = fields.Float(
        string="Decoupled Lead Time (days)",
        compute="_compute_dlt",
    )
    context_location_id = fields.Many2one(
        comodel_name="stock.location",
        string="Stock Location",
        compute="_compute_context_location",
    )

    def _get_search_buffer_domain(self):
        product = self.product_id
        if not product and self.product_tmpl_id.product_variant_ids:
            product = self.product_tmpl_id.product_variant_ids[0]
        domain = [
            ("product_id", "=", product.id),
            ("location_id", "=", self.context_location_id.id),
        ]
        if self.company_id:
            domain.append(("company_id", "=", self.company_id.id))
        return domain

    @api.depends("product_id", "product_tmpl_id", "context_location_id")
    def _compute_buffer(self):
        for record in self:
            domain = record._get_search_buffer_domain()
            # NOTE: It can be possible to find multiple buffers.
            # For example if the BoM has no location set, and there
            # are buffers with the same product_id and buffer_profile_id
            # You do not know which one the search function finds.
            buffer = self.env["stock.buffer"].search(domain, limit=1)
            record.buffer_id = buffer

    @api.depends("buffer_id")
    def _compute_is_buffered(self):
        for bom in self:
            bom.is_buffered = True if bom.buffer_id else False

    @api.depends_context("location_id")
    def _compute_context_location(self):
        warehouse_model = self.env["stock.warehouse"]
        for rec in self:
            if self.env.context.get("location_id", None):
                rec.context_location_id = self.env.context.get("location_id")
            elif self.env.context.get("warehouse", None):
                warehouse_id = self.env.context.get("warehouse")
                rec.context_location_id = warehouse_model.browse(
                    warehouse_id
                ).lot_stock_id.id
            else:
                company_id = rec.company_id or self.env.company
                warehouse_id = warehouse_model.search(
                    [("company_id", "=", company_id.id)], limit=1
                )
                rec.context_location_id = warehouse_id.lot_stock_id.id

    def _get_produce_delay(self):
        self.ensure_one()
        return self.produce_delay

    def _get_longest_path(self):
        if not self.bom_line_ids:
            return 0.0
        paths = [0] * len(self.bom_line_ids)
        i = 0
        for line in self.bom_line_ids:
            if line.is_buffered:
                i += 1
            elif line.product_id.bom_ids:
                # If the a component is manufactured we continue exploding.
                location = line.context_location_id
                line_boms = line.product_id.bom_ids
                bom = line_boms.filtered(
                    lambda bom: bom.context_location_id == location  # noqa: B023
                ) or line_boms.filtered(lambda bom: not bom.context_location_id)
                if bom:
                    paths[i] += bom[0]._get_produce_delay()
                    paths[i] += bom[0]._get_longest_path()
                else:
                    _logger.info(
                        "ddmrp (dlt): Product {} has no BOM for location " "{}.".format(
                            line.product_id.name, location.name
                        )
                    )
                i += 1
            else:
                # assuming they are purchased,
                if line.product_id.seller_ids:
                    paths[i] = line.product_id.seller_ids[0].delay
                else:
                    _logger.info(
                        "ddmrp (dlt): Product %s has no seller set."
                        % line.product_id.name
                    )
                i += 1
        return max(paths)

    def _get_manufactured_dlt(self):
        """Computes the Decoupled Lead Time exploding all the branches of the
        BOM until a buffered position and then selecting the greatest."""
        self.ensure_one()
        dlt = self._get_produce_delay()
        dlt += self._get_longest_path()
        return dlt

    @api.depends("context_location_id")
    @api.depends_context("location_id")
    def _compute_dlt(self):
        for rec in self:
            rec.dlt = rec._get_manufactured_dlt()

    def action_change_context_location(self):
        return {
            "type": "ir.actions.act_window",
            "name": _("Change MRP BoM Location"),
            "res_model": "mrp.bom.change.location",
            "view_mode": "form",
            "target": "new",
        }


class MrpBomLine(models.Model):
    _inherit = "mrp.bom.line"

    is_buffered = fields.Boolean(
        string="Buffered?",
        compute="_compute_is_buffered",
        help="True when the product has an DDMRP buffer associated.",
    )
    buffer_id = fields.Many2one(
        comodel_name="stock.buffer",
        string="Stock Buffer",
        compute="_compute_is_buffered",
    )
    dlt = fields.Float(
        string="Decoupled Lead Time (days)",
        compute="_compute_dlt",
    )
    context_location_id = fields.Many2one(related="bom_id.context_location_id")

    def _get_search_buffer_domain(self):
        product = self.product_id
        if not product and self.product_tmpl_id.product_variant_ids:
            product = self.product_tmpl_id.product_variant_ids[0]
        domain = [
            ("product_id", "=", product.id),
            ("location_id", "=", self.context_location_id.id),
        ]
        if self.company_id:
            domain.append(("company_id", "=", self.company_id.id))
        return domain

    @api.depends("context_location_id")
    @api.depends_context("location_id")
    def _compute_is_buffered(self):
        for line in self:
            domain = line._get_search_buffer_domain()
            buffer = self.env["stock.buffer"].search(domain, limit=1)
            line.buffer_id = buffer
            line.is_buffered = True if buffer else False

    @api.depends("product_id")
    def _compute_dlt(self):
        for rec in self:
            if rec.product_id.bom_ids:
                rec.dlt = rec.product_id.bom_ids[0].dlt
            else:
                rec.dlt = (
                    rec.product_id.seller_ids
                    and rec.product_id.seller_ids[0].delay
                    or 0.0
                )
