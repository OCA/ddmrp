# Copyright 2018 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models, tools
from odoo.addons import decimal_precision as dp
UNIT = dp.get_precision('Product Unit of Measure')


class ReportDdmrpPartsPlanFlowIndex(models.Model):
    _name = 'report.ddmrp.part.plan.flow.index'
    _auto = False

    orderpoint_id = fields.Many2one('stock.warehouse.orderpoint',
                                    string='Buffer',
                                    readonly=True)
    product_id = fields.Many2one('product.product',
                                 string='Product',
                                 readonly=True)
    location_id = fields.Many2one('stock.location',
                                  string='Location',
                                  readonly=True)
    adu = fields.Float(string="Average Daily Usage (ADU)",
                       default=0.0, digits=UNIT, readonly=True)
    green_zone_qty = fields.Float(string="Green Zone Qty",
                                  digits=UNIT, readonly=True)
    order_frequency = fields.Float(string="Order Frequency",
                                   digits=UNIT, readonly=True)
    order_frequency_group = fields.Integer(string="Order Frequency Group",
                                           readonly=True)
    order_frequency_group_count = fields.Integer(
        string="Order Frequency Group Count", readonly=True)
    flow_index_group_id = fields.Many2one(
        'ddmrp.flow.index.group', string="Flow Index Group", readonly=True)

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self._cr,
                                  'report_ddmrp_part_plan_flow_index')
        self._cr.execute(
            """
            CREATE or REPLACE VIEW report_ddmrp_part_plan_flow_index AS (
                WITH a AS
                    (SELECT
                        id,
                        product_id,
                        location_id,
                        adu,
                        flow_index_group_id,
                        green_zone_qty,
                        green_zone_qty/NULLIF(adu, 0) as order_frequency,
                        round(green_zone_qty/NULLIF(adu, 0)) AS
                        order_frequency_group
                     FROM stock_warehouse_orderpoint
                    )
                SELECT
                    a.id as id,
                    a.id as orderpoint_id,
                    a.product_id as product_id,
                    a.location_id as location_id,
                    a.adu as adu,
                    a.flow_index_group_id as flow_index_group_id,
                    a.green_zone_qty as green_zone_qty,
                    a.order_frequency as order_frequency,
                    a.order_frequency_group as order_frequency_group,
                    b.order_frequency_group_count
                FROM a
                JOIN (SELECT
                        order_frequency_group, count(*) AS
                        order_frequency_group_count
                       FROM a
                       GROUP BY order_frequency_group
                      ) AS b
                ON a.order_frequency_group = b.order_frequency_group
                )
            """
        )
