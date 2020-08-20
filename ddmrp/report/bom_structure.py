# Copyright 2017-20 ForgeFlow S.L. (http://www.forgeflow.com)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, models


class BomStructureReport(models.AbstractModel):
    _inherit = "report.mrp.mrp_bom_structure_report"

    @api.model
    def _get_child_vals(self, record, level, qty, uom):
        res = super()._get_child_vals(record, level, qty, uom)
        if record.product_id.bom_ids:
            lead_time = record.product_id.produce_delay
        else:
            lead_time = (
                record.product_id.seller_ids
                and record.product_id.seller_ids[0].delay
                or 0.0
            )
        res["is_buffered"] = record.is_buffered
        res["has_mto_rule"] = record.has_mto_rule
        res["lead_time"] = lead_time or ""
        res["dlt"] = record.dlt
        return res
