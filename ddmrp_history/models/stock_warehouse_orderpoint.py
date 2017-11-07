# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import logging
from math import pi

from openerp import api, fields, models, _
from datetime import datetime
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT

_logger = logging.getLogger(__name__)
try:
    import numpy as np
    import pandas as pd
    from bokeh.plotting import figure
    from bokeh.embed import components
    from bokeh.models import HoverTool, DatetimeTickFormatter
except (ImportError, IOError) as err:
    _logger.debug(err)


class StockWarehouseOrderpoint(models.Model):
    _inherit = "stock.warehouse.orderpoint"

    def _prepare_history_data(self):
        self.ensure_one()
        data = {
            'orderpoint_id': self.id,
            'date': datetime.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
            'top_of_red': self.top_of_red,
            'top_of_yellow': self.top_of_yellow,
            'top_of_green': self.top_of_green,
            'net_flow_position': self.net_flow_position,
            'on_hand_position': self.product_location_qty,
        }
        return data

    @api.multi
    def cron_actions(self):
        res = super(StockWarehouseOrderpoint, self).cron_actions()
        data = self._prepare_history_data()
        self.env['ddmrp.history'].sudo().create(data)
        return res

    def _compute_history_chart(self):
        def stacked(df, categories):
            areas = dict()
            last = np.zeros(len(df[categories[0]]))
            for cat in categories:
                next = last + df[cat]
                areas[cat] = np.hstack((last[::-1], next))
                last = next
            return areas

        for rec in self:
            history = self.env['ddmrp.history'].search([
                ('orderpoint_id', '=', rec.id)], order='date')
            if len(history) < 2:
                rec.history_chart = _("Not enough data available.")
                continue

            N = len(history)
            categories = ['top_of_red', 'top_of_yellow', 'top_of_green']
            data = {}

            dates = [datetime.strptime(
                r.date, DEFAULT_SERVER_DATETIME_FORMAT) for r in history]
            data['date'] = dates
            data[categories[0]] = [r.top_of_red for r in history]
            data[categories[1]] = [r.top_of_yellow -
                                   r.top_of_red for r in history]
            data[categories[2]] = [r.top_of_green -
                                   r.top_of_yellow for r in history]
            data['net_flow_position'] = [r.net_flow_position for r in history]
            data['on_hand_position'] = [r.on_hand_position for r in history]

            df = pd.DataFrame(data)
            df = df.set_index(['date'])

            areas = stacked(df, categories)

            # FIXME: create a get_colors method for share color from the two
            # charst in ddmpr.
            colors = ['#ff0000', '#ffff00', '#33cc33']

            x2 = np.hstack((data['date'][::-1], data['date']))

            tops = [data[categories[0]][i] + data[categories[1]][i] +
                    data[categories[2]][i] for i in range(N)]
            top_y = max(tops)
            p = figure(
                x_range=(dates[0], dates[-1]), y_range=(0, top_y),
                x_axis_type='datetime')

            p.grid.minor_grid_line_color = '#eeeeee'
            p.patches([x2] * len(areas), [areas[cat] for cat in categories],
                      color=colors, alpha=0.8, line_color=None)
            p.xaxis.formatter = DatetimeTickFormatter(
                hours=["%d %B %Y"], days=["%d %B %Y"], months=["%d %B %Y"],
                years=["%d %B %Y"])
            p.xaxis.major_label_orientation = pi / 4

            unit = rec.product_uom.name
            hover = HoverTool(tooltips=[("qty", "$y %s" % unit)],
                              point_policy='follow_mouse')
            p.add_tools(hover)

            p.line(dates, data['net_flow_position'], line_width=3)
            p.line(dates, data['on_hand_position'], line_width=3,
                   line_dash='dotted')

            script, div = components(p)
            rec.history_chart = '%s%s' % (div, script)


    # TODO: store false and computed through a button?
    history_chart = fields.Text(
        string='Historical Chart', compute='_compute_history_chart')
