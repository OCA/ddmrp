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

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        records._calc_execution_priority()
        return records

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
