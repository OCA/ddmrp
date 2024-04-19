# Copyright 2017-24 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class StockBuffer(models.Model):
    _inherit = "stock.buffer"

    flow_index_group_id = fields.Many2one(
        "ddmrp.flow.index.group", string="Flow Index Group", readonly=True
    )

    def _calc_flow_index_group_id(self):
        flow_index_reports = self.env["report.ddmrp.part.plan.flow.index"].read_group(
            domain=[("buffer_id", "in", self.ids)],
            fields=["order_frequency_group"],
            groupby=["buffer_id"],
        )
        flow_index_groups = self.env["ddmrp.flow.index.group"].search([])
        for rec in self:
            flow_index_report = list(
                filter(lambda x: x["buffer_id"][0] == rec.id, flow_index_reports)
            )
            if not flow_index_report:
                continue

            frequency_group = flow_index_report[0]["order_frequency_group"]
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
