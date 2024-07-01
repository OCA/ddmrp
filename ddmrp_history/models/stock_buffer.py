# Copyright 2017-20 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

import json
import logging
from math import pi

from odoo import _, fields, models

_logger = logging.getLogger(__name__)
try:
    import numpy as np
    import pandas as pd
    from bokeh.embed import components
    from bokeh.models import DatetimeTickFormatter, HoverTool
    from bokeh.plotting import figure
except (OSError, ImportError) as err:
    _logger.debug(err)


class StockBuffer(models.Model):
    _inherit = "stock.buffer"

    planning_history_chart = fields.Text(
        string="Historical Chart",
        compute="_compute_history_chart",
    )
    execution_history_chart = fields.Text(
        string="Execution Historical Chart",
        compute="_compute_execution_history_chart",
    )

    def _prepare_history_data(self):
        self.ensure_one()
        data = {
            "buffer_id": self.id,
            "date": fields.Datetime.now(),
            "top_of_red": self.top_of_red,
            "top_of_yellow": self.top_of_yellow,
            "top_of_green": self.top_of_green,
            "net_flow_position": self.net_flow_position,
            "on_hand_position": self.product_location_qty_available_not_res,
            "adu": self.adu,
        }
        return data

    def cron_actions(self, only_nfp=False):
        res = super().cron_actions(only_nfp=only_nfp)
        data = self._prepare_history_data()
        if not self.env.context.get("no_ddmrp_history"):
            self.env["ddmrp.history"].sudo().create(data)
        return res

    def _compute_history_chart(self):
        def stacked(df, categories):
            areas = {}
            last = np.zeros(len(df[categories[0]]))
            for cat in categories:
                _next = last + df[cat]
                areas[cat] = np.hstack((last[::-1], _next))
                last = _next
            return areas

        hex_colors = self._get_colors_hex_map(pallete="planning")
        planning_colors = [
            hex_colors["1_red"],
            hex_colors["2_yellow"],
            hex_colors["3_green"],
        ]
        for rec in self:
            history = self.env["ddmrp.history"].search(
                [("buffer_id", "=", rec.id)], order="date"
            )
            if len(history) < 2:
                rec.planning_history_chart = json.dumps(
                    {
                        "div": _("Not enough data available."),
                        "script": "",
                    }
                )
                continue

            N = len(history)
            categories = ["top_of_red", "top_of_yellow", "top_of_green"]
            data = {}

            dates = [r.date for r in history]
            data["date"] = dates
            data[categories[0]] = [r.top_of_red for r in history]
            data[categories[1]] = [r.top_of_yellow - r.top_of_red for r in history]
            data[categories[2]] = [r.top_of_green - r.top_of_yellow for r in history]
            data["net_flow_position"] = [r.net_flow_position for r in history]
            data["on_hand_position"] = [r.on_hand_position for r in history]

            df = pd.DataFrame(data)
            df = df.set_index(["date"])

            areas = stacked(df, categories)

            x2 = np.hstack((data["date"][::-1], data["date"]))

            tops = [
                data[categories[0]][i] + data[categories[1]][i] + data[categories[2]][i]
                for i in range(N)
            ] + [max(data["on_hand_position"]), max(data["net_flow_position"])]
            top_y = max(tops)
            min_y = min(
                [0, min(data["on_hand_position"]), min(data["net_flow_position"])]
            )
            if top_y <= min_y:
                top_y = min_y + 100
            p = figure(
                frame_height=400,
                x_range=(dates[0], dates[-1]),
                y_range=(min_y, top_y),
                x_axis_type="datetime",
            )
            p.sizing_mode = "stretch_width"
            p.toolbar.logo = None

            p.grid.minor_grid_line_color = "#eeeeee"
            p.patches(
                [x2] * len(areas),
                [areas[cat] for cat in categories],
                color=planning_colors,
                alpha=0.8,
                line_color=None,
            )
            date_format = (
                self.env["res.lang"]._lang_get(self.env.lang or "en_US").date_format
            )
            p.xaxis.formatter = DatetimeTickFormatter(
                hours=date_format,
                days=date_format,
                months=date_format,
                years=date_format,
            )
            p.xaxis.major_label_orientation = pi / 4
            p.xaxis.axis_label_text_font = "helvetica"

            unit = rec.product_uom.name
            hover = HoverTool(
                tooltips=[("qty", "$y %s" % unit)], point_policy="follow_mouse"
            )
            p.add_tools(hover)

            p.line(dates, data["net_flow_position"], line_width=3)
            p.line(dates, data["on_hand_position"], line_width=3, line_dash="dotted")

            script, div = components(p, wrap_script=False)
            json_data = json.dumps(
                {
                    "div": div,
                    "script": script,
                }
            )
            rec.planning_history_chart = json_data

    def _compute_execution_history_chart(self):
        start_stack = 0

        def stacked(df, categories):
            areas = {}
            last = np.zeros(len(df[categories[0]]))
            last += start_stack
            for cat in categories:
                _next = last + df[cat]
                areas[cat] = np.hstack((last[::-1], _next))
                last = _next
            return areas

        hex_colors = self._get_colors_hex_map(pallete="execution")
        execution_colors = [
            hex_colors["0_dark_red"],
            hex_colors["1_red"],
            hex_colors["2_yellow"],
            hex_colors["3_green"],
            hex_colors["2_yellow"],
            hex_colors["1_red"],
            hex_colors["0_dark_red"],
        ]
        history_model = self.env["ddmrp.history"]
        for rec in self:
            domain = [("buffer_id", "=", rec.id)]
            history_oh = history_model.search(
                domain, order="on_hand_position desc", limit=1
            )
            history_tog = history_model.search(
                domain + [("top_of_green", "!=", False)],
                order="top_of_green desc",
                limit=1,
            )
            finish_stack = max(history_oh.on_hand_position, history_tog.top_of_green)

            history = history_model.search(
                domain, order="on_hand_position asc", limit=1
            )
            start_stack = history.on_hand_position
            if start_stack >= 0.0:
                start_stack = 0.0
            history = history_model.search(domain, order="date")
            if len(history) < 2:
                rec.execution_history_chart = json.dumps(
                    {
                        "div": _("Not enough data available."),
                        "script": "",
                    }
                )
                continue

            N = len(history)

            categories = [
                "dark_red_low",
                "top_of_red_low",
                "top_of_yellow_low",
                "top_of_green",
                "top_of_yellow",
                "top_of_red",
                "dark_red",
            ]
            data = {}

            dates = [r.date for r in history]
            data["date"] = dates
            data[categories[0]] = [(0 - start_stack) for r in history]
            data[categories[1]] = [(r.top_of_red / 2) for r in history]
            data[categories[2]] = [(r.top_of_red / 2) for r in history]
            data[categories[3]] = [r.top_of_green - r.top_of_yellow for r in history]
            data[categories[4]] = [
                (r.top_of_green - r.top_of_red - (r.top_of_green - r.top_of_yellow)) / 2
                for r in history
            ]
            data[categories[5]] = [
                (r.top_of_green - r.top_of_red - (r.top_of_green - r.top_of_yellow)) / 2
                for r in history
            ]
            data[categories[6]] = [
                finish_stack
                - r.top_of_red
                - (r.top_of_green - r.top_of_yellow)
                - (r.top_of_green - r.top_of_red - (r.top_of_green - r.top_of_yellow))
                for r in history
            ]

            data["on_hand_position"] = [r.on_hand_position for r in history]

            df = pd.DataFrame(data)
            df = df.set_index(["date"])

            areas = stacked(df, categories)

            x2 = np.hstack((data["date"][::-1], data["date"]))

            tops = [
                data[categories[0]][i]
                + data[categories[1]][i]
                + data[categories[2]][i]
                + data[categories[3]][i]
                + data[categories[4]][i]
                + data[categories[5]][i]
                + data[categories[6]][i]
                for i in range(N)
            ]
            top_y = max(tops)
            p = figure(
                frame_height=400,
                x_range=(dates[0], dates[-1]),
                y_range=(start_stack, top_y or 100),
                x_axis_type="datetime",
            )
            p.sizing_mode = "stretch_width"
            p.toolbar.logo = None

            p.grid.minor_grid_line_color = "#eeeeee"
            p.patches(
                [x2] * len(areas),
                [areas[cat] for cat in categories],
                color=execution_colors,
                alpha=0.8,
                line_color=None,
            )
            date_format = (
                self.env["res.lang"]._lang_get(self.env.lang or "en_US").date_format
            )
            p.xaxis.formatter = DatetimeTickFormatter(
                hours=date_format,
                days=date_format,
                months=date_format,
                years=date_format,
            )
            p.xaxis.major_label_orientation = pi / 4

            unit = rec.product_uom.name
            hover = HoverTool(
                tooltips=[("qty", "$y %s" % unit)], point_policy="follow_mouse"
            )
            p.add_tools(hover)

            p.line(dates, data["on_hand_position"], line_width=3, line_dash="dotted")

            script, div = components(p, wrap_script=False)
            json_data = json.dumps(
                {
                    "div": div,
                    "script": script,
                }
            )
            rec.execution_history_chart = json_data
