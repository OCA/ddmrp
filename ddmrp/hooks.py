# Copyright 2018 ForgeFlow S.L. (http://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import _

from odoo.addons.mrp.report.mrp_report_bom_structure import ReportBomStructure


def post_load_hook():
    def new_get_pdf_line(
        self, bom_id, product_id=False, qty=1, child_bom_ids=None, unfolded=False
    ):

        if not hasattr(self, "_get_line_vals"):
            return self._get_pdf_line(
                self,
                bom_id,
                product_id=False,
                qty=1,
                child_bom_ids=None,
                unfolded=False,
            )

        data = self._get_bom(bom_id=bom_id, product_id=product_id, line_qty=qty)

        def new_get_sub_lines(bom, product_id, line_qty, line_id, level):
            data = self._get_bom(
                bom_id=bom.id,
                product_id=product_id,
                line_qty=line_qty,
                line_id=line_id,
                level=level,
            )
            bom_lines = data["components"]
            lines = []
            for bom_line in bom_lines:
                line_vals = self._get_line_vals(bom_line)
                lines.append(line_vals)
                if bom_line["child_bom"] and (
                    unfolded or bom_line["child_bom"] in child_bom_ids
                ):
                    line = self.env["mrp.bom.line"].browse(bom_line["line_id"])
                    lines += new_get_sub_lines(
                        line.child_bom_id,
                        line.product_id,
                        bom_line["prod_qty"],
                        line,
                        level + 1,
                    )
            if data["operations"]:
                lines.append(
                    {
                        "name": _("Operations"),
                        "type": "operation",
                        "quantity": data["operations_time"],
                        "uom": _("minutes"),
                        "bom_cost": data["operations_cost"],
                        "level": level,
                    }
                )
                for operation in data["operations"]:
                    if unfolded or "operation-" + str(bom.id) in child_bom_ids:
                        lines.append(
                            {
                                "name": operation["name"],
                                "type": "operation",
                                "quantity": operation["duration_expected"],
                                "uom": _("minutes"),
                                "bom_cost": operation["total"],
                                "level": level + 1,
                            }
                        )
            return lines

        bom = self.env["mrp.bom"].browse(bom_id)
        product = product_id or bom.product_id or bom.product_tmpl_id.product_variant_id
        pdf_lines = new_get_sub_lines(bom, product, qty, False, 1)
        data["components"] = []
        data["lines"] = pdf_lines
        return data

    if not hasattr(ReportBomStructure, "_get_pdf_line_original"):
        ReportBomStructure._get_pdf_line_original = ReportBomStructure._get_pdf_line
        ReportBomStructure._get_pdf_line = new_get_pdf_line
