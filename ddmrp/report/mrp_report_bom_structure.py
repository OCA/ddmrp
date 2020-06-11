# Copyright 2017-20 ForgeFlow S.L. (http://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, models


class BomStructureReport(models.AbstractModel):
    _inherit = "report.mrp.report_bom_structure"

    @api.model
    def _get_bom_lines(self, bom, bom_quantity, product, line_id, level):
        res = super(BomStructureReport, self)._get_bom_lines(
            bom, bom_quantity, product, line_id, level
        )
        line_ids = self.env["mrp.bom.line"].search([("bom_id", "=", bom.id)])
        for line in res[0]:
            line_id = line_ids.browse(line["line_id"])
            if line_id.product_id.bom_ids:
                lead_time = line_id.product_id.produce_delay
            else:
                lead_time = (
                    line_id.product_id.seller_ids
                    and line_id.product_id.seller_ids[0].delay
                    or 0.0
                )
            line["is_buffered"] = line_id.is_buffered
            line["lead_time"] = lead_time or 0
            line["dlt"] = line_id.dlt
        return res

    def _get_line_vals(self, bom_line):
        line = self.env["mrp.bom.line"].browse(bom_line["line_id"])
        if line.product_id.bom_ids:
            lead_time = line.product_id.produce_delay or 0
        else:
            lead_time = (
                line.product_id.seller_ids and line.product_id.seller_ids[0].delay
            ) or 0
        return {
            "name": bom_line["prod_name"],
            "type": "bom",
            "quantity": bom_line["prod_qty"],
            "uom": bom_line["prod_uom"],
            "prod_cost": bom_line["prod_cost"],
            "bom_cost": bom_line["total"],
            "level": bom_line["level"],
            "code": bom_line["code"],
            "is_buffered": bom_line["is_buffered"],
            "lead_time": lead_time,
            "dlt": bom_line["dlt"],
        }
