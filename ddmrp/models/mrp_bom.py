# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models


class MrpBom(models.Model):
    _inherit = "mrp.bom"

    def _get_search_buffer_domain(self):
        product = self.product_id or \
                  self.product_tmpl_id.product_variant_ids[0]
        domain = [('product_id', '=', product.id),
                  ('buffer_profile_id', '!=', False)]
        if self.location_id:
            domain.append(('location_id', '=', self.location_id.id))
        return domain

    def _compute_buffered(self):
        for bom in self:
            domain = bom._get_search_buffer_domain()
            orderpoint = self.env['stock.warehouse.orderpoint'].search(
                domain, limit=1)
            bom.orderpoint_id = orderpoint
            bom.buffered = True if orderpoint else False

    buffered = fields.Boolean(
        string="Buffered?", compute="_compute_buffered",
        help="True when the product has an DDMRP buffer associated.")

    orderpoint_id = fields.Many2one(
        comodel_name='stock.warehouse.orderpoint', string='Orderpoint',
        compute="_compute_buffered")


class MrpBom(models.Model):
    _inherit = "mrp.bom.line"

    def _get_search_buffer_domain(self):
        product = self.product_id or \
                  self.product_tmpl_id.product_variant_ids[0]
        domain = [('product_id', '=', product.id),
                  ('buffer_profile_id', '!=', False)]
        if self.location_id:
            domain.append(('location_id', '=', self.location_id.id))
        return domain

    def _compute_buffered(self):
        for line in self:
            domain = line._get_search_buffer_domain()
            orderpoint = self.env['stock.warehouse.orderpoint'].search(
                domain, limit=1)
            line.orderpoint_id = orderpoint
            line.buffered = True if orderpoint else False

    buffered = fields.Boolean(
        string="Buffered?", compute="_compute_buffered",
        help="True when the product has an DDMRP buffer associated.")

    orderpoint_id = fields.Many2one(
        comodel_name='stock.warehouse.orderpoint', string='Orderpoint',
        compute="_compute_buffered")
