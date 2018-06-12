# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
from openerp import api, fields, models
_logger = logging.getLogger(__name__)


class MrpBom(models.Model):
    _inherit = "mrp.bom"

    is_buffered = fields.Boolean(
        string="Buffered?", compute="_compute_is_buffered",
        help="True when the product has an DDMRP buffer associated.",
    )
    orderpoint_id = fields.Many2one(
        comodel_name='stock.warehouse.orderpoint', string='Orderpoint',
        compute="_compute_orderpoint",
    )
    dlt = fields.Float(
        string="Decoupled Lead Time (days)",
        compute="_compute_dlt",
    )
    has_mto_rule = fields.Boolean(
        string="MTO",
        help="Follows an MTO Pull Rule",
        compute="_compute_mto_rule",
    )

    def _get_search_buffer_domain(self):
        product = self.product_id
        if not product:
            if self.product_tmpl_id.product_variant_ids:
                product = self.product_tmpl_id.product_variant_ids[0]
        domain = [('product_id', '=', product.id),
                  ('buffer_profile_id', '!=', False)]
        if self.location_id:
            domain.append(('location_id', '=', self.location_id.id))
        return domain

    @api.depends('product_id', 'product_tmpl_id', 'location_id')
    def _compute_orderpoint(self):
        for record in self:
            domain = record._get_search_buffer_domain()
            # NOTE: It can be possible to find multiple orderpoints.
            # For example if the BoM has no location set, and there
            # are orderpoints with the same product_id and buffer_profile_id
            # You do not know which one the search function finds.
            orderpoint = self.env['stock.warehouse.orderpoint'].search(
                domain, limit=1)
            record.orderpoint_id = orderpoint

    @api.depends('orderpoint_id')
    def _compute_is_buffered(self):
        for bom in self:
            bom.is_buffered = True if bom.orderpoint_id else False

    @api.depends('location_id')
    def _compute_mto_rule(self):
        # TODO: fix
        for rec in self:
            rec.has_mto_rule = False

    @api.multi
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
                location = line.location_id
                line_boms = line.product_id.bom_ids
                bom = line_boms.filtered(
                    lambda bom: bom.location_id == location) or \
                    line_boms.filtered(lambda bom: not bom.location_id)
                if bom:
                    produce_delay = bom[0].product_id.produce_delay or \
                        bom[0].product_tmpl_id.produce_delay
                    paths[i] += produce_delay
                    paths[i] += bom[0]._get_longest_path()
                else:
                    _logger.info(
                        "ddmrp (dlt): Product %s has no BOM for location "
                        "%s." % (line.product_id.name, location.name))
                i += 1
            else:
                # assuming they are purchased,
                if line.product_id.seller_ids:
                    paths[i] = line.product_id.seller_ids[0].delay
                else:
                    _logger.info(
                        "ddmrp (dlt): Product %s has no seller set." %
                        line.product_id.name)
                i += 1
        return max(paths)

    @api.multi
    def _get_manufactured_dlt(self):
        """Computes the Decoupled Lead Time exploding all the branches of the
        BOM until a buffered position and then selecting the greatest."""
        self.ensure_one()
        dlt = self.product_id.produce_delay or \
            self.product_tmpl_id.produce_delay
        dlt += self._get_longest_path()
        return dlt

    def _compute_dlt(self):
        for rec in self:
            rec.dlt = rec._get_manufactured_dlt()


class MrpBomLine(models.Model):
    _inherit = "mrp.bom.line"

    is_buffered = fields.Boolean(
        string="Buffered?", compute="_compute_is_buffered",
        help="True when the product has an DDMRP buffer associated.",
    )
    orderpoint_id = fields.Many2one(
        comodel_name='stock.warehouse.orderpoint', string='Orderpoint',
        compute="_compute_is_buffered",
    )
    dlt = fields.Float(
        string="Decoupled Lead Time (days)",
        compute="_compute_dlt",
    )
    has_mto_rule = fields.Boolean(
        string="MTO",
        help="Follows an MTO Pull Rule",
        compute="_compute_mto_rule",
    )

    def _get_search_buffer_domain(self):
        product = self.product_id or \
            self.product_tmpl_id.product_variant_ids[0]
        domain = [('product_id', '=', product.id),
                  ('buffer_profile_id', '!=', False)]
        if self.location_id:
            domain.append(('location_id', '=', self.location_id.id))
        return domain

    def _compute_is_buffered(self):
        for line in self:
            domain = line._get_search_buffer_domain()
            orderpoint = self.env['stock.warehouse.orderpoint'].search(
                domain, limit=1)
            line.orderpoint_id = orderpoint
            line.is_buffered = True if orderpoint else False

    @api.depends('product_id')
    def _compute_dlt(self):
        for rec in self:
            if rec.product_id.bom_ids:
                rec.dlt = rec.product_id.bom_ids[0].dlt
            else:
                rec.dlt = rec.product_id.seller_ids and \
                    rec.product_id.seller_ids[0].delay or 0.0

    @api.depends('location_id')
    def _compute_mto_rule(self):
        for rec in self:
            rec.has_mto_rule = False
