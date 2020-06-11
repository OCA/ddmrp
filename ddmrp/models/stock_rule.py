# Copyright 2018 Camptocamp (https://www.camptocamp.com)
# Copyright 2019-20 ForgeFlow S.L. (http://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import models


class StockRule(models.Model):
    _inherit = "stock.rule"

    def _prepare_mo_vals(
        self,
        product_id,
        product_qty,
        product_uom,
        location_id,
        name,
        origin,
        company_id,
        values,
        bom,
    ):
        result = super(StockRule, self)._prepare_mo_vals(
            product_id,
            product_qty,
            product_uom,
            location_id,
            name,
            origin,
            company_id,
            values,
            bom,
        )
        # TODO: stock_orderpoint_mrp_link: tests!
        if "buffer_id" in values:
            result["buffer_id"] = values["buffer_id"].id
        elif "buffer_ids" in values:
            # We take the always first value as in case of chain procurements,
            # the procurements are resolved first and then the moves are
            # merged. Thus here we are going to have only one buffer in
            # in buffer_ids.
            result["buffer_id"] = values["buffer_ids"][0].id
        return result

    def _run_manufacture(self, procurements):
        super()._run_manufacture(procurements)
        for procurement, _rule in procurements:
            buffer = procurement.values.get("buffer_id")
            if buffer:
                buffer.sudo().cron_actions()
        return True

    # TODO: stock_orderpoint_move_link: tests!
    def _get_stock_move_values(
        self,
        product_id,
        product_qty,
        product_uom,
        location_id,
        name,
        origin,
        values,
        group_id,
    ):
        vals = super()._get_stock_move_values(
            product_id,
            product_qty,
            product_uom,
            location_id,
            name,
            origin,
            values,
            group_id,
        )
        if "buffer_id" in values:
            vals["buffer_ids"] = [(4, values["buffer_id"].id)]
        elif "buffer_ids" in values:
            vals["buffer_ids"] = [(4, o.id) for o in values["buffer_ids"]]
        return vals

    def _prepare_purchase_order_line(
        self, product_id, product_qty, product_uom, company_id, values, po
    ):
        vals = super()._prepare_purchase_order_line(
            product_id, product_qty, product_uom, company_id, values, po
        )
        # If the procurement was run directly by a reordering rule.
        if "buffer_id" in values:
            vals["buffer_ids"] = [(4, values["buffer_id"].id)]
        # If the procurement was run by a stock move.
        elif "buffer_ids" in values:
            vals["buffer_ids"] = [(4, o.id) for o in values["buffer_ids"]]
        return vals

    def _update_purchase_order_line(
        self, product_id, product_qty, product_uom, company_id, values, line
    ):
        vals = super()._update_purchase_order_line(
            product_id, product_qty, product_uom, company_id, values, line
        )
        if "buffer_id" in values:
            vals["buffer_ids"] = [(4, values["buffer_id"].id)]
        # If the procurement was run by a stock move.
        elif "buffer_ids" in values:
            vals["buffer_ids"] = [(4, o.id) for o in values["buffer_ids"]]
        return vals
