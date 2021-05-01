# Copyright 2020 KMEE
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
import statistics
from odoo import api, fields, models, _
from odoo.addons.ddmrp.models.stock_buffer_profile import (
    _ITEM_TYPES,
    _REPLENISH_METHODS,
)

_logger = logging.getLogger(__name__)


try:
    import numpy as np
    import pandas as pd
    import plotly
    from bokeh.plotting import figure
    from bokeh.embed import components
    from bokeh.models import HoverTool, DatetimeTickFormatter
except (ImportError, IOError) as err:
    _logger.debug(err)


class DdmrpSimulationProduct(models.Model):

    _name = 'ddmrp.simulation.product'
    _description = 'Ddmrp Simulation Product'

    @api.depends('simulation_id', 'product_id')
    def _compute_line_ids(self):
        for record in self:
            record.line_ids = record.line_ids.search([
                ('simulation_id', '=', record.simulation_id.id),
                ('product_id', '=', record.product_id.id),
            ], order="date")

    def button_statistics(self):
        for record in self:

            history = self.env["ddmrp.history"].search(
                [("buffer_id", "=", record.stock_buffer_id.id)], order="date"
            )

            if len(history) < 2:
                continue

            data = {}
            dates = [r.date for r in history]
            data["date"] = dates
            data["on_hand_position"] = [r.on_hand_position for r in history]
            data["on_hand_simulation"] = [r.on_hand_simulation for r in history]

            df = pd.DataFrame(data)
            df = df.set_index(["date"])

            df_by_date_min = df.resample('1D').min()
            df_by_date_max = df.resample('1D').max()
            df_by_date_avg = df.resample('1D').mean()

            days_stock_out_current = df_by_date_min[
                df_by_date_min.on_hand_simulation <= 0].size
            days_stock_out_simulation = df_by_date_min[
                df_by_date_min.on_hand_position <= 0].size

            data_lines = {}

            dates = [r.date for r in record.line_ids]
            data_lines["date"] = dates

            data_lines["demand"] = [r.demand for r in record.line_ids]
            data_lines["on_hand"] = [r.on_hand for r in record.line_ids]

            df_data_lines = pd.DataFrame(data_lines)
            df_data_lines = df_data_lines.set_index(["date"])

            results = [
                (6, 0, {}),
                (0, 0, {
                    'code': 'average_on_hand',
                    'name': 'Average On Hand - QTY',
                    'current': df['on_hand_simulation'].mean(),
                    'simulation': df['on_hand_position'].mean(),
                }),
                (0, 0, {
                    'code': 'average_on_hand_value',
                    'name': 'Average On Hand - Value ($)',
                    'current': df['on_hand_simulation'].mean() * record.standard_price,
                    'simulation':
                        df['on_hand_position'].mean() * record.standard_price,
                }),
                (0, 0, {
                    'code': 'total_demand',
                    'name': 'Total Demand',
                    'current': df_data_lines['demand'].sum(),
                    'simulation': df_data_lines['demand'].sum(),
                }),
                (0, 0, {
                    'code': 'turnover',
                    'name': 'Average Turnover',
                    'current':
                        df_data_lines['demand'].sum() * record.standard_price
                            / df['on_hand_simulation'].mean(),
                    'simulation': df_data_lines['demand'].sum() * record.standard_price
                            / df['on_hand_position'].mean(),
                }),
                (0, 0, {
                    'code': 'peak_demand',
                    'name': 'Peak Demand',
                    'current': df_data_lines['demand'].max(),
                    'simulation': df_data_lines['demand'].max(),
                }),
                (0, 0, {
                    'code': 'supply_orders',
                    'name': 'Supply Orders',
                    'current': 0,  # TODO:
                    'simulation': len(record.stock_buffer_id.purchase_line_ids),
                }),
                (0, 0, {
                    'code': 'average_order_size',
                    'name': 'Average Order Size',
                    'current': 0,  # Data not available
                    'simulation': statistics.mean(
                        record.stock_buffer_id.purchase_line_ids.mapped('product_qty')
                    ),
                }),
                (0, 0, {
                    'code': 'minimum_on_hand',
                    'name': 'Minimum On Hand',
                    'current': df['on_hand_simulation'].min(),
                    'simulation': df['on_hand_position'].min(),
                }),
                (0, 0, {
                    'code': 'max_on_hand',
                    'name': 'Max On Hand',
                    'current': df['on_hand_simulation'].max(),
                    'simulation': df['on_hand_position'].max(),
                }),
                (0, 0, {
                    'code': 'service_level',
                    'name': 'Service Level',
                    'current':
                        (1 - (days_stock_out_current/df_by_date_avg.size)) * 100,
                    'simulation':
                        (1 - (days_stock_out_simulation/df_by_date_avg.size)) * 100,
                }),
                (0, 0, {
                    'code': 'days_stock_out',
                    'name': 'Days Stock Out',
                    'current': days_stock_out_current,
                    'simulation': days_stock_out_simulation,
                }),
            ]

            pd.options.plotting.backend = "plotly"

            demand_histogram = plotly.offline.plot(
                df_data_lines['demand'].hist(),
                include_plotlyjs=False,
                output_type='div'
            )
            on_hand_simulation_histogram = plotly.offline.plot(
                df[['on_hand_simulation','on_hand_position']].hist(),
                include_plotlyjs=False,
                output_type='div'
            )
            record.write({
                'result_ids': results,
                'demand_histogram': demand_histogram,
                'on_hand_simulation_histogram': on_hand_simulation_histogram,
            })

    simulation_id = fields.Many2one(
        comodel_name='ddmrp.simulation',
        required=True,
    )
    product_tmpl_id = fields.Many2one(
        comodel_name='product.template',
        related='product_id.product_tmpl_id'
    )
    product_id = fields.Many2one(
        comodel_name='product.product',
    )
    reference = fields.Char(
        related='product_id.default_code',
        store=True,
        readonly=False,
    )
    name = fields.Char(
        related='product_id.name',
        store=True,
        readonly=False,
    )
    standard_price = fields.Float(
        related='product_id.standard_price',
        store=True,
        readonly=False,
    )
    seller_id = fields.Many2one(
        comodel_name='product.supplierinfo',
    )
    lead_time = fields.Integer(
        related='seller_id.delay',
        store=True,
        readonly=False,
    )
    replenish_method = fields.Selection(
        string="Replenishment method",
        selection=_REPLENISH_METHODS,
        default='replenish',
        required=True,
    )
    item_type = fields.Selection(
        string="Item Type",
        selection=_ITEM_TYPES,
        default='purchased',
        required=True,
    )
    lead_time_id = fields.Many2one(
        comodel_name="stock.buffer.profile.lead.time",
        string="Lead Time Factor",
        default=lambda self:
            self.env.ref('ddmrp.stock_buffer_profile_lead_time_medium')
    )
    variability_id = fields.Many2one(
        comodel_name='stock.buffer.profile.variability',
        default=lambda self:
            self.env.ref('ddmrp.stock_buffer_profile_variability_medium')
    )
    adu_calculation_method = fields.Many2one(
        comodel_name="product.adu.calculation.method",
        string="ADU calculation method",
        required=True,
        default=lambda self:
            self.env.ref('ddmrp.adu_calculation_method_fixed')
    )
    stock_buffer_id = fields.Many2one(
        comodel_name='stock.buffer',
    )

    line_ids = fields.One2many(
        comodel_name='ddmrp.simulation.line',
        compute='_compute_line_ids',
        string='Lines'
    )
    result_ids = fields.One2many(
        comodel_name='ddmrp.simulation.product.result',
        inverse_name='simulation_product_id',
        string='Results'
    )
    demand_histogram = fields.Text()
    on_hand_simulation_histogram = fields.Text()

    def action_view_related_lines(self):
        self.ensure_one()
        domain = [
            ('simulation_id', '=', self.simulation_id.id),
            ('product_id', '=', self.product_id.id),
        ]
        action = {
            'name': _('Simulation Lines'),
            'type': 'ir.actions.act_window',
            'res_model': 'ddmrp.simulation.line',
            'view_type': 'list',
            'view_mode': 'list,form',
            'domain': domain,
        }
        return action
