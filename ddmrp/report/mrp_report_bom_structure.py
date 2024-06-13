# Copyright 2017-23 ForgeFlow S.L. (http://www.forgeflow.com)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, models


class BomStructureReport(models.AbstractModel):
    _inherit = "report.mrp.report_bom_structure"

    def _get_pdf_doc(self, bom_id, data, quantity, product_variant_id=None):
        doc = super()._get_pdf_doc(bom_id, data, quantity, product_variant_id)
        doc["show_buffered"] = (
            True if data and data.get("show_buffered") == "true" else False
        )
        return doc

    @api.model
    def _get_bom_data(
        self,
        bom,
        warehouse,
        product=False,
        line_qty=False,
        bom_line=False,
        level=0,
        parent_bom=False,
        parent_product=False,
        index=0,
        product_info=False,
        ignore_stock=False,
    ):
        res = super()._get_bom_data(
            bom,
            warehouse,
            product=product,
            line_qty=line_qty,
            bom_line=bom_line,
            level=level,
            parent_bom=parent_bom,
            parent_product=parent_product,
            index=index,
            product_info=product_info,
            ignore_stock=ignore_stock,
        )
        res["is_buffered"] = bom.is_buffered
        res["dlt"] = bom.dlt
        return res

    def _get_component_data(
        self,
        parent_bom,
        parent_product,
        warehouse,
        bom_line,
        line_quantity,
        level,
        index,
        product_info,
        ignore_stock=False,
    ):
        res = super()._get_component_data(
            parent_bom,
            parent_product,
            warehouse,
            bom_line,
            line_quantity,
            level,
            index,
            product_info,
            ignore_stock=ignore_stock,
        )
        if bom_line.product_id.bom_ids:
            lead_time = bom_line.bom_id.produce_delay
        else:
            lead_time = (
                bom_line.product_id.seller_ids
                and bom_line.product_id.seller_ids[0].delay
                or 0.0
            )
        res["is_buffered"] = bom_line.is_buffered
        res["lead_time"] = lead_time or False
        res["dlt"] = bom_line.dlt
        return res

    def _get_bom_array_lines(
        self, data, level, unfolded_ids, unfolded, parent_unfolded
    ):
        lines = super()._get_bom_array_lines(
            data, level, unfolded_ids, unfolded, parent_unfolded
        )
        for component in data.get("components", []):
            if not component["bom_id"]:
                continue
            bom_line = next(
                filter(
                    lambda line: line.get("bom_id", None) == component["bom_id"], lines
                )
            )
            if bom_line:
                bom_line["is_buffered"] = component["is_buffered"]
                bom_line["dlt"] = component["dlt"]
        return lines
