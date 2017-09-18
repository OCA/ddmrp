# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import logging

from openerp import api, fields, models, _

_logger = logging.getLogger(__name__)


class StockWarehouseOrderpoint(models.Model):
    _inherit = "stock.warehouse.orderpoint"

    @api.multi
    def _calc_adu(self):
        """Apply DAFs if existing for the buffer."""
        res = super(StockWarehouseOrderpoint, self)._calc_adu()
        today = fields.Date.today()
        adjustments = self.env['ddmrp.adjustment'].search([
            ('buffer_id', '=', self.id), ('daf', '>', 0.0),
            ('date_range_id.date_start', '<=', today),
            ('date_range_id.date_end', '>=', today)])
        if adjustments:
            daf = 1
            values = adjustments.mapped('daf')
            for val in values:
                daf *= val
            prev = self.adu
            self.adu *= daf
            # TODO: change to debug when tested.
            _logger.info(
                "DAF=%s applied to %s. ADU: %s -> %s" %
                (daf, self.name, prev, self.adu))
            # Compute generated demand to be applied to components:
            increased_demand = self.adu - prev
            self.explode_demand_to_components(
                increased_demand, self.product_uom)
        return res

    extra_demand_ids = fields.One2many(
        comodel_name="ddmrp.adjustment.demand", string="Extra Demand",
        inverse_name="buffer_id",
        help="Demand associated to Demand Adjustment Factors applied to "
             "parent buffers.")

    def _get_init_bom(self):
        # TODO: This is on pull/13 and its the correct method. Need to adapt
        # when 13 gets merge.
        # init_bom = self.env['mrp.bom'].search([
        #     '|',
        #     ('product_id', '=', self.product_id.id),
        #     ('product_tmpl_id', '=', self.product_id.product_tmpl_id.id),
        #     '|',
        #     ('location_id', '=', self.location_id.id),
        #     ('location_id', '=', False)], limit=1)
        # return init_bom
        self.ensure_one()
        init_bom = self.env['mrp.bom'].search([
            '|',
            ('product_id', '=', self.product_id.id),
            ('product_tmpl_id', '=', self.product_id.product_tmpl_id.id)
        ], limit=1)
        return init_bom

    def explode_demand_to_components(self, demand, uom_id):
        uom_obj = self.env['product.uom']
        demand_obj = self.env['ddmrp.adjustment.demand']
        init_bom = self._get_init_bom()
        if not init_bom:
            return

        def _get_extra_demand(bom, line, buffer_id, factor):
            qty = factor * line.product_qty / bom.product_qty
            extra = uom_obj._compute_qty_obj(
                line.product_uom, qty, buffer_id.product_uom)
            return extra

        def _create_demand(bom, factor=1, level=0):
            level += 1
            for line in bom.bom_line_ids:
                buffer_id = self.search([
                    ('product_id', '=', line.product_id.id)], limit=1)  # TODO: pull/13: filter by location also
                if buffer_id:  # TODO: In #13 the buffered flag is added to bom
                    extra_demand = _get_extra_demand(
                        bom, line, buffer_id, factor)
                    existing = demand_obj.search([
                        ('buffer_id', '=', buffer_id.id),
                        ('buffer_origin_id', '=', self.id)], limit=1)
                    if existing:
                        existing.sudo().write({'extra_demand': extra_demand})
                    else:
                        demand_obj.sudo().create({
                            'buffer_id': buffer_id.id,
                            'buffer_origin_id': self.id,
                            'extra_demand': extra_demand,
                        })
                # location = line.location_id  # TODO: pull/13: with locations:
                line_boms = line.product_id.bom_ids
                # bom = line_boms.filtered(
                #     lambda bom: bom.location_id == location) or \
                #     line_boms.filtered(lambda b: not b.location_id) # TODO: pull/13: with locations:
                child_bom = line_boms
                if child_bom:
                    line_qty = uom_obj._compute_qty_obj(
                        line.product_uom, line.product_qty,
                        child_bom.product_uom)
                    new_factor = factor * line_qty / bom.product_qty
                    _create_demand(child_bom[0], new_factor, level)

        initial_factor = uom_obj._compute_qty_obj(
            uom_id, demand, init_bom.product_uom)
        _create_demand(init_bom, factor=initial_factor)
        return True

    @api.model
    def cron_ddmrp_adu(self, automatic=False):
        """Apply extra demand originated by Demand Adjustment Factors to
        components after the cron update of all the buffers."""
        self.env['ddmrp.adjustment.demand'].search([]).unlink()
        super(StockWarehouseOrderpoint, self).cron_ddmrp_adu(automatic)
        for op in self.search([]).filtered('extra_demand_ids'):
            op.adu += sum(op.extra_demand_ids.mapped('extra_demand'))
            _logger.info("DAFs-originated demand applied.")

    @api.multi
    def action_view_demand_to_components(self):
        demand_ids = self.env["ddmrp.adjustment.demand"].search([
            ('buffer_origin_id', '=', self.id)]).ids
        return {
            "name": _("Demand Allocated to Components"),
            "type": "ir.actions.act_window",
            "res_model": "ddmrp.adjustment.demand",
            "view_type": "form",
            "view_mode": "tree",
            "domain": [('id', 'in', demand_ids)],
        }
