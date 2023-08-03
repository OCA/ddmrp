# Copyright 2016-20 ForgeFlow S.L. (http://www.forgeflow.com)
# Copyright 2016 Aleph Objects, Inc. (https://www.alephobjects.com/)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models

from .stock_buffer import _PRIORITY_LEVEL


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    buffer_id = fields.Many2one(
        comodel_name="stock.buffer",
        index=True,
        string="Stock Buffer",
    )
    execution_priority_level = fields.Selection(
        string="Buffer On-Hand Alert Level",
        selection=_PRIORITY_LEVEL,
        readonly=True,
    )
    on_hand_percent = fields.Float(
        string="On Hand/TOR (%)",
    )

    @api.model
    def create(self, vals):
        record = super(MrpProduction, self).create(vals)
        record._find_buffer_link()
        record._calc_execution_priority()
        return record

    def write(self, vals):
        res = super().write(vals)
        if any(
            f in vals
            for f in ("product_id", "picking_type_id", "location_dest_id", "company_id")
        ):
            self._find_buffer_link()
        return res

    def _get_domain_buffer_link(self, warehouse_level=False):
        self.ensure_one()
        domain = [
            ("product_id", "=", self.product_id.id),
            ("company_id", "=", self.company_id.id),
            ("buffer_profile_id.item_type", "=", "manufactured"),
        ]
        if not warehouse_level:
            locations = self.env["stock.location"].search(
                [("id", "child_of", [self.location_dest_id.id])]
            )
            domain += [("location_id", "in", locations.ids)]
        else:
            domain += [("warehouse_id", "=", self.picking_type_id.warehouse_id.id)]
        return domain

    def _find_buffer_link(self):
        buffer_model = self.env["stock.buffer"]
        for rec in self:
            domain = rec._get_domain_buffer_link()
            buffer = buffer_model.search(domain, limit=1)
            if not buffer:
                domain = rec._get_domain_buffer_link(warehouse_level=True)
                buffer = buffer_model.search(domain, limit=1)
            rec.buffer_id = buffer
            if buffer:
                rec._calc_execution_priority()

    def _calc_execution_priority(self):
        """Technical note: this method cannot be decorated with api.depends,
        otherwise it would generate a infinite recursion."""
        prods = self.filtered(
            lambda r: r.buffer_id and r.state not in ["done", "cancel"]
        )
        for rec in prods:
            rec.execution_priority_level = rec.buffer_id.execution_priority_level
            rec.on_hand_percent = rec.buffer_id.on_hand_percent
        to_update = (self - prods).filtered(
            lambda r: r.execution_priority_level or r.on_hand_percent
        )
        if to_update:
            to_update.write({"execution_priority_level": None, "on_hand_percent": None})

    def _search_execution_priority(self, operator, value):
        """Search on the execution priority by evaluating on all
        open manufacturing orders."""
        all_records = self.search([("state", "not in", ["done", "cancel"])])

        if operator == "=":
            found_ids = [
                a.id for a in all_records if a.execution_priority_level == value
            ]
        elif operator == "in" and isinstance(value, list):
            found_ids = [
                a.id for a in all_records if a.execution_priority_level in value
            ]
        elif operator in ("!=", "<>"):
            found_ids = [
                a.id for a in all_records if a.execution_priority_level != value
            ]
        elif operator == "not in" and isinstance(value, list):
            found_ids = [
                a.id for a in all_records if a.execution_priority_level not in value
            ]
        else:
            raise NotImplementedError(
                "Search operator {} not implemented for value {}".format(
                    operator, value
                )
            )
        return [("id", "in", found_ids)]
