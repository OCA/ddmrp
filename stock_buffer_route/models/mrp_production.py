# Copyright 2023 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    def _get_domain_buffer_link_alternative(self, warehouse_level=False):
        self.ensure_one()
        if not warehouse_level:
            locations = self.env["stock.location"].search(
                [("id", "child_of", [self.location_dest_id.id])]
            )
            return [
                ("product_id", "=", self.product_id.id),
                ("company_id", "=", self.company_id.id),
                ("item_type_alternative", "=", "manufactured"),
                ("location_id", "in", locations.ids),
            ]
        else:
            return [
                ("product_id", "=", self.product_id.id),
                ("company_id", "=", self.company_id.id),
                ("item_type_alternative", "=", "manufactured"),
                ("warehouse_id", "=", self.picking_type_id.warehouse_id.id),
            ]

    def _find_buffer_link(self):
        res = super()._find_buffer_link()
        buffer_model = self.env["stock.buffer"]
        for rec in self.filtered(lambda r: not r.buffer_id):
            domain = rec._get_domain_buffer_link_alternative()
            buffer = buffer_model.search(domain, limit=1)
            if not buffer:
                domain = rec._get_domain_buffer_link_alternative(warehouse_level=True)
                buffer = buffer_model.search(domain, limit=1)
            rec.buffer_id = buffer
            if buffer:
                rec._calc_execution_priority()
        return res
