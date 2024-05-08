# Copyright 2017-24 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo import api, fields, models


class ReportDdmrpPartsPlanFlowIndex(models.Model):
    _name = "report.ddmrp.part.plan.flow.index"
    _auto = False

    buffer_id = fields.Many2one("stock.buffer", string="Buffer", readonly=True)
    product_id = fields.Many2one("product.product", string="Product", readonly=True)
    location_id = fields.Many2one("stock.location", string="Location", readonly=True)
    company_id = fields.Many2one("res.company", string="Company", readonly=True)
    adu = fields.Float(
        string="Average Daily Usage (ADU)",
        default=0.0,
        digits="Average Daily Usage",
        readonly=True,
    )
    green_zone_qty = fields.Float(digits="Product Unit of Measure", readonly=True)
    order_frequency = fields.Float(digits="Product Unit of Measure", readonly=True)
    order_frequency_group = fields.Integer(readonly=True)
    order_frequency_group_count = fields.Integer(readonly=True)
    flow_index_group_id = fields.Many2one(
        "ddmrp.flow.index.group", string="Flow Index Group", readonly=True
    )

    @api.model
    def _sub_select(self):
        select_str = """
            id,
            product_id,
            location_id,
            company_id,
            adu,
            flow_index_group_id,
            green_zone_qty,
            green_zone_qty/NULLIF(adu, 0) as order_frequency,
            round(green_zone_qty/NULLIF(adu, 0)) AS
            order_frequency_group
        """
        return select_str

    @api.model
    def _select(self):
        select_str = """
            a.id as id,
            a.id as buffer_id,
            a.product_id as product_id,
            a.location_id as location_id,
            a.company_id as company_id,
            a.adu as adu,
            a.flow_index_group_id as flow_index_group_id,
            a.green_zone_qty as green_zone_qty,
            a.order_frequency as order_frequency,
            a.order_frequency_group as order_frequency_group,
            b.order_frequency_group_count
        """
        return select_str

    @api.model
    def _join_select(self):
        select_str = """
            order_frequency_group,
            count(*) AS order_frequency_group_count
        """
        return select_str

    @property
    def _table_query(self):
        return """
                WITH a AS
                    (SELECT %s
                     FROM stock_buffer)
                SELECT
                    %s
                FROM a
                JOIN (SELECT
                        %s
                       FROM a
                       GROUP BY order_frequency_group
                      ) AS b
                ON a.order_frequency_group = b.order_frequency_group
            """ % (
            self._sub_select(),
            self._select(),
            self._join_select(),
        )
