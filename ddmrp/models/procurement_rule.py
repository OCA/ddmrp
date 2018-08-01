# Copyright 2018 Camptocamp (https://www.camptocamp.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models


class ProcurementRule(models.Model):
    _inherit = 'procurement.rule'

    def _prepare_mo_vals(self, product_id, product_qty, product_uom,
                         location_id, name, origin, values, bom):
        result = super(ProcurementRule, self)._prepare_mo_vals(
            product_id, product_qty, product_uom, location_id,
            name, origin, values, bom
        )
        # this field can be passed by
        # StockWarehouseOrderpoint._prepare_procurement_values
        # (yes as a recordset!)
        if values.get('orderpoint_id'):
            result['orderpoint_id'] = values['orderpoint_id'].id
        return result

    def _run_manufacture(self, product_id, product_qty, product_uom,
                         location_id, name, origin, values):
        super(ProcurementRule, self)._run_manufacture(
            product_id, product_qty, product_uom,
            location_id, name, origin, values
        )
        orderpoint = values.get('orderpoint_id')
        if orderpoint:
            orderpoint.cron_actions()
        return True
