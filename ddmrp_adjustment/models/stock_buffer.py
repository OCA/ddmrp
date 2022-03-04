# Copyright 2017-20 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import logging
from datetime import timedelta as td

from odoo import _, api, fields, models

from ..models.ddmrp_adjustment import DAF_string, LTAF_string

_logger = logging.getLogger(__name__)


class StockBuffer(models.Model):
    _inherit = "stock.buffer"

    extra_demand_ids = fields.One2many(
        comodel_name="ddmrp.adjustment.demand",
        string="Extra Demand",
        inverse_name="buffer_id",
        help="Demand associated to Demand Adjustment Factors applied to "
        "parent buffers.",
    )

    def _daf_to_apply_domain(self, current=True):
        self.ensure_one()
        today = fields.Date.today()
        domain = [
            ("buffer_id", "=", self.id),
            ("adjustment_type", "=", DAF_string),
            ("date_range_id.date_end", ">=", today),
        ]
        if current:
            domain.append(("date_range_id.date_start", "<=", today))
        return domain

    def _calc_adu(self):
        """Apply DAFs if existing for the buffer."""
        res = super()._calc_adu()
        self.ensure_one()
        dafs_to_apply = self.env["ddmrp.adjustment"].search(self._daf_to_apply_domain())
        if dafs_to_apply:
            daf = 1
            values = dafs_to_apply.mapped("value")
            for val in values:
                daf *= val
            prev = self.adu
            self.adu *= daf
            _logger.debug(
                "DAF={} applied to {}. ADU: {} -> {}".format(
                    daf, self.name, prev, self.adu
                )
            )
        # Compute generated demand to be applied to components:
        dafs_to_explode = self.env["ddmrp.adjustment"].search(
            self._daf_to_apply_domain(False)
        )
        for daf in dafs_to_explode:
            prev = self.adu
            increased_demand = prev * daf.value - prev
            self.explode_demand_to_components(daf, increased_demand, self.product_uom)
        return res

    def explode_demand_to_components(self, daf, demand, uom_id):
        demand_obj = self.env["ddmrp.adjustment.demand"]
        init_bom = self._get_manufactured_bom()
        if not init_bom:
            return

        def _get_extra_demand(bom, line, buffer_id, factor):
            qty = factor * line.product_qty / bom.product_qty
            extra = line.product_uom_id._compute_quantity(qty, buffer_id.product_uom)
            return extra

        def _create_demand(bom, factor=1, level=0, clt=0):
            level += 1
            produce_delay = (
                bom[0].product_id.produce_delay or bom[0].product_tmpl_id.produce_delay
            )
            clt += produce_delay
            for line in bom.bom_line_ids:
                if line.is_buffered:
                    buffer_id = line.buffer_id
                    extra_demand = _get_extra_demand(bom, line, buffer_id, factor)
                    date_start = daf.date_range_id.date_start - td(days=clt)
                    date_end = daf.date_range_id.date_end - td(days=clt)
                    demand_obj.sudo().create(
                        {
                            "buffer_id": buffer_id.id,
                            "buffer_origin_id": self.id,
                            "extra_demand": extra_demand,
                            "date_start": date_start,
                            "date_end": date_end,
                        }
                    )
                location = line.location_id
                line_boms = line.product_id.bom_ids
                child_bom = line_boms.filtered(
                    lambda bom: bom.location_id == location
                ) or line_boms.filtered(lambda b: not b.location_id)
                if child_bom:
                    line_qty = line.product_uom_id._compute_quantity(
                        line.product_qty, child_bom.product_uom_id
                    )
                    new_factor = factor * line_qty / bom.product_qty
                    _create_demand(child_bom[0], new_factor, level, clt)

        initial_factor = uom_id._compute_quantity(demand, init_bom.product_uom_id)
        _create_demand(init_bom, factor=initial_factor)
        return True

    @api.model
    def cron_ddmrp_adu(self, automatic=False):
        """Apply extra demand originated by Demand Adjustment Factors to
        components after the cron update of all the buffers."""
        self.env["ddmrp.adjustment.demand"].search([]).unlink()
        res = super().cron_ddmrp_adu(automatic)
        today = fields.Date.today()
        for op in self.search([]).filtered("extra_demand_ids"):
            to_add = sum(
                op.extra_demand_ids.filtered(
                    lambda r: r.date_start <= today <= r.date_end
                ).mapped("extra_demand")
            )
            if to_add:
                op.adu += to_add
                _logger.debug(
                    "DAFs-originated demand applied. {}: ADU += {}".format(
                        op.name, to_add
                    )
                )
        return res

    def _ltaf_to_apply_domain(self):
        self.ensure_one()
        today = fields.Date.today()
        return [
            ("buffer_id", "=", self.id),
            ("adjustment_type", "=", LTAF_string),
            ("date_range_id.date_start", "<=", today),
            ("date_range_id.date_end", ">=", today),
        ]

    def _compute_dlt(self):
        """Apply Lead Time Adj Factor if existing"""
        res = super()._compute_dlt()
        for rec in self:
            ltaf_to_apply = self.env["ddmrp.adjustment"].search(
                rec._ltaf_to_apply_domain()
            )
            if ltaf_to_apply:
                ltaf = 1
                values = ltaf_to_apply.mapped("value")
                for val in values:
                    ltaf *= val
                prev = rec.dlt
                rec.dlt *= ltaf
                _logger.debug(
                    "LTAF=%s applied to %s. DLT: %s -> %s"
                    % (ltaf, rec.name, prev, rec.dlt)
                )
        return res

    def action_view_demand_to_components(self):
        demand_ids = (
            self.env["ddmrp.adjustment.demand"]
            .search([("buffer_origin_id", "=", self.id)])
            .ids
        )
        return {
            "name": _("Demand Allocated to Components"),
            "type": "ir.actions.act_window",
            "res_model": "ddmrp.adjustment.demand",
            "view_mode": "tree",
            "domain": [("id", "in", demand_ids)],
        }
