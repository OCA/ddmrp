# Copyright 2017-24 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class StockBuffer(models.Model):
    _inherit = "stock.buffer"

    flow_index_group_id = fields.Many2one(
        "ddmrp.flow.index.group", string="Flow Index Group", readonly=True
    )

    def _calc_flow_index_group_id(self):
        self.env["stock.buffer"].flush_model()
        frequency_by_buffer = dict(
            self.env["report.ddmrp.part.plan.flow.index"]._read_group(
                domain=[("buffer_id", "in", self.ids)],
                groupby=["buffer_id"],
                aggregates=["order_frequency_group:sum"],
            )
        )
        flow_index_groups = self.env["ddmrp.flow.index.group"].search([])  # pylint: disable=no-search-all
        for rec in self:
            if rec not in frequency_by_buffer:
                continue

            frequency_group = frequency_by_buffer[rec]
            for index_group in flow_index_groups:
                if index_group.upper_range and index_group.lower_range:
                    if (
                        index_group.lower_range
                        <= frequency_group
                        <= index_group.upper_range
                    ):
                        rec.flow_index_group_id = index_group
                        break
                elif index_group.upper_range:
                    if index_group.upper_range >= frequency_group:
                        rec.flow_index_group_id = index_group
                        break
                elif index_group.lower_range:
                    if frequency_group >= index_group.lower_range:
                        rec.flow_index_group_id = index_group
                        break

    def cron_actions(self, only_nfp=False):
        res = super().cron_actions(only_nfp=only_nfp)
        self._calc_flow_index_group_id()
        return res
