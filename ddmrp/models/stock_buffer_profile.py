# Copyright 2016-20 ForgeFlow S.L. (http://www.forgeflow.com)
# Copyright 2016 Aleph Objects, Inc. (https://www.alephobjects.com/)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models

_REPLENISH_METHODS = [
    ("replenish", "Replenished"),
    ("replenish_override", "Replenished Override"),
    ("min_max", "Min-max"),
]
_ITEM_TYPES = [
    ("manufactured", "Manufactured"),
    ("purchased", "Purchased"),
    ("distributed", "Distributed"),
]


class StockBufferProfile(models.Model):
    _name = "stock.buffer.profile"
    _description = "Stock Buffer Profile"

    @api.depends(
        "item_type",
        "lead_time_id",
        "lead_time_id.name",
        "lead_time_id.factor",
        "variability_id",
        "variability_id.name",
        "variability_id.factor",
        "distributed_reschedule_max_proc_time",
    )
    def _compute_name(self):
        """Get the right summary for this job."""
        for rec in self:
            name = "{} {}, {}({}), {}({})".format(
                rec.replenish_method,
                rec.item_type,
                rec.lead_time_id.name,
                rec.lead_time_id.factor,
                rec.variability_id.name,
                rec.variability_id.factor,
            )
            if rec.distributed_reschedule_max_proc_time > 0.0:
                name += f", {rec.distributed_reschedule_max_proc_time}min"
            rec.name = name

    name = fields.Char(compute="_compute_name", store=True)
    replenish_method = fields.Selection(
        string="Replenishment method", selection=_REPLENISH_METHODS, required=True
    )
    item_type = fields.Selection(selection=_ITEM_TYPES, required=True)
    lead_time_id = fields.Many2one(
        comodel_name="stock.buffer.profile.lead.time", string="Lead Time Factor"
    )
    variability_id = fields.Many2one(
        comodel_name="stock.buffer.profile.variability", string="Variability Factor"
    )
    company_id = fields.Many2one(
        "res.company",
        "Company",
    )

    replenish_distributed_limit_to_free_qty = fields.Boolean(
        string="Limit replenishment to free quantity",
        default=False,
        help="When activated, the recommended quantity will be maxed at "
        "the quantity available in the replenishment source location.",
    )
    distributed_reschedule_max_proc_time = fields.Float(
        string="Re-Schedule Procurement Max Proc. Time (minutes)",
        default=0.0,
        help="When you request procurement from a buffer, their scheduled"
        " date is rescheduled to now + this procurement time (in minutes)."
        " Their scheduled date represents the latest the transfers should"
        " be done, and therefore, past this timestamp, considered late.",
    )
