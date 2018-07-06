# Copyright 2016-18 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# Copyright 2016 Aleph Objects, Inc. (https://www.alephobjects.com/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import logging

from odoo import api, fields, models, _
from datetime import datetime, timedelta
from odoo.addons import decimal_precision as dp
from odoo.tools import float_compare, float_round
import operator as py_operator

_logger = logging.getLogger(__name__)
try:
    from bokeh.plotting import figure
    from bokeh.embed import components
    from bokeh.models import Legend, ColumnDataSource, LabelSet
except (ImportError, IOError) as err:
    _logger.debug(err)


OPERATORS = {
    '<': py_operator.lt,
    '>': py_operator.gt,
    '<=': py_operator.le,
    '>=': py_operator.ge,
    '==': py_operator.eq,
    '!=': py_operator.ne
}


UNIT = dp.get_precision('Product Unit of Measure')


_PRIORITY_LEVEL = [
    ('1_red', 'Red'),
    ('2_yellow', 'Yellow'),
    ('3_green', 'Green')
]


class StockWarehouseOrderpoint(models.Model):
    _inherit = 'stock.warehouse.orderpoint'
    _description = "Stock Buffer"

    @api.multi
    @api.depends("dlt", "adu", "buffer_profile_id.lead_time_id.factor",
                 "buffer_profile_id.variability_id.factor",
                 "product_uom.rounding", "red_override",
                 "lead_days", "product_id.seller_ids.delay")
    def _compute_red_zone(self):
        for rec in self:
            if rec.replenish_method in ['replenish', 'min_max']:
                rec.red_base_qty = float_round(
                    rec.dlt * rec.adu *
                    rec.buffer_profile_id.lead_time_id.factor,
                    precision_rounding=rec.product_uom.rounding)
                rec.red_safety_qty = float_round(
                    rec.red_base_qty *
                    rec.buffer_profile_id.variability_id.factor,
                    precision_rounding=rec.product_uom.rounding)
                rec.red_zone_qty = rec.red_base_qty + rec.red_safety_qty
            else:
                rec.red_zone_qty = rec.red_override

    @api.multi
    @api.depends("dlt", "adu", "buffer_profile_id.lead_time_id.factor",
                 "order_cycle", "minimum_order_quantity",
                 "product_uom.rounding", "green_override")
    def _compute_green_zone(self):
        for rec in self:
            if rec.replenish_method in ['replenish', 'min_max']:
                # Using imposed or desired minimum order cycle
                rec.green_zone_oc = float_round(
                    rec.order_cycle * rec.adu,
                    precision_rounding=rec.product_uom.rounding)
                # Using lead time factor
                rec.green_zone_lt_factor = float_round(
                    rec.dlt*rec.adu*rec.buffer_profile_id.lead_time_id.factor,
                    precision_rounding=rec.product_uom.rounding)
                # Using minimum order quantity
                rec.green_zone_moq = float_round(
                    rec.minimum_order_quantity,
                    precision_rounding=rec.product_uom.rounding)

                # The biggest option of the above will be used as the green
                # zone value
                rec.green_zone_qty = max(rec.green_zone_oc,
                                         rec.green_zone_lt_factor,
                                         rec.green_zone_moq)
            else:
                rec.green_zone_qty = rec.green_override
            rec.top_of_green = \
                rec.green_zone_qty + rec.yellow_zone_qty + rec.red_zone_qty

    @api.multi
    @api.depends("dlt", "adu", "buffer_profile_id.lead_time_id.factor",
                 "buffer_profile_id.variability_id.factor",
                 "buffer_profile_id.replenish_method",
                 "order_cycle", "minimum_order_quantity",
                 "product_uom.rounding", "yellow_override",
                 "red_zone_qty")
    def _compute_yellow_zone(self):
        for rec in self:
            if rec.replenish_method == 'min_max':
                rec.yellow_zone_qty = 0
            elif rec.replenish_method == 'replenish':
                rec.yellow_zone_qty = float_round(
                    rec.dlt * rec.adu,
                    precision_rounding=rec.product_uom.rounding)
            else:
                rec.yellow_zone_qty = rec.yellow_override
            rec.top_of_yellow = rec.yellow_zone_qty + rec.red_zone_qty

    @api.multi
    @api.depends("dlt")
    def _compute_procure_recommended_date(self):
        for rec in self:
            dlt = int(rec.dlt)
            # For purchased items we always consider calendar days,
            # not work days.
            if rec.warehouse_id.calendar_id and rec.buffer_profile_id and \
                    rec.buffer_profile_id.item_type != 'purchased':
                dt_to = rec.warehouse_id.calendar_id.plan_days(
                    dlt + 1, datetime.now())
                procure_recommended_date = fields.Date.to_string(dt_to)
            else:
                procure_recommended_date = \
                    fields.date.today() + timedelta(days=dlt)
            rec.procure_recommended_date = procure_recommended_date

    @api.multi
    @api.depends("net_flow_position", "dlt", "adu",
                 "buffer_profile_id.lead_time_id.factor",
                 "red_zone_qty", "order_cycle", "minimum_order_quantity",
                 "qty_multiple", "product_uom", "procure_uom_id",
                 "product_uom.rounding")
    def _compute_procure_recommended_qty(self):
        subtract_qty = self._quantity_in_progress()
        for rec in self:
            procure_recommended_qty = 0.0
            if rec.net_flow_position < rec.top_of_yellow:
                qty = (rec.top_of_green -
                       rec.net_flow_position -
                       subtract_qty[rec.id])
                if qty >= 0.0:
                    procure_recommended_qty = qty
            else:
                if subtract_qty[rec.id] > 0.0:
                    procure_recommended_qty -= subtract_qty[rec.id]
            if procure_recommended_qty > 0.0:
                reste = rec.qty_multiple > 0 and \
                    procure_recommended_qty % rec.qty_multiple or 0.0

                if rec.procure_uom_id:
                    rounding = rec.procure_uom_id.rounding
                else:
                    rounding = rec.product_uom.rounding

                if float_compare(
                        reste, 0.0,
                        precision_rounding=rounding) > 0:
                    procure_recommended_qty += rec.qty_multiple - reste

                if rec.procure_uom_id:
                    product_qty = rec.product_id.uom_id._compute_quantity(
                        procure_recommended_qty, rec.procure_uom_id)
                else:
                    product_qty = procure_recommended_qty
            else:
                product_qty = 0.0

            rec.procure_recommended_qty = product_qty

    def _compute_ddmrp_chart(self):
        """This method use the Bokeh library to create a buffer depiction."""
        for rec in self:
            p = figure(plot_width=300, plot_height=400,
                       y_axis_label='Quantity')
            p.xaxis.visible = False
            red = p.vbar(x=1, bottom=0, top=rec.top_of_red, width=1,
                         color='red', legend=False)
            yellow = p.vbar(x=1, bottom=rec.top_of_red, top=rec.top_of_yellow,
                            width=1, color='yellow', legend=False)
            green = p.vbar(x=1, bottom=rec.top_of_yellow, top=rec.top_of_green,
                           width=1, color='green', legend=False)
            net_flow = p.line(
                [0, 2], [rec.net_flow_position, rec.net_flow_position],
                line_width=2)
            on_hand = p.line(
                [0, 2], [rec.product_location_qty, rec.product_location_qty],
                line_width=2, line_dash='dotted')
            legend = Legend(items=[
                ("Red zone", [red]),
                ("Yellow zone", [yellow]),
                ("Green zone", [green]),
                ("Net Flow Position", [net_flow]),
                ("On-Hand Position", [on_hand]),
            ])
            labels_source_data = {
                'height': [rec.net_flow_position,
                           rec.product_location_qty,
                           rec.top_of_red,
                           rec.top_of_yellow,
                           rec.top_of_green],
                'weight': [0.25, 1.75, 1, 1, 1],
                'names': [rec.net_flow_position,
                          rec.product_location_qty,
                          rec.top_of_red,
                          rec.top_of_yellow,
                          rec.top_of_green],
            }
            source = ColumnDataSource(data=labels_source_data)
            labels = LabelSet(
                x="weight", y="height", text="names", y_offset=1,
                render_mode='canvas', text_font_size="8pt",
                source=source, text_align='center')
            p.add_layout(labels)
            p.add_layout(legend, 'below')

            script, div = components(p)
            rec.ddmrp_chart = '%s%s' % (div, script)

    @api.multi
    @api.depends("red_zone_qty")
    def _compute_order_spike_threshold(self):
        # TODO: Add various methods to compute the spike threshold
        for rec in self:
            rec.order_spike_threshold = 0.5 * rec.red_zone_qty

    def _get_manufactured_bom(self):
        return self.env['mrp.bom'].search(
            ['|',
             ('product_id', '=', self.product_id.id),
             ('product_tmpl_id', '=', self.product_id.product_tmpl_id.id),
             '|',
             ('location_id', '=', self.location_id.id),
             ('location_id', '=', False)], limit=1)

    @api.depends('lead_days', 'product_id.seller_ids.delay')
    def _compute_dlt(self):
        for rec in self:
            if rec.buffer_profile_id.item_type == 'manufactured':
                bom = rec._get_manufactured_bom()
                rec.dlt = bom.dlt
            elif rec.buffer_profile_id.item_type == 'distributed':
                rec.dlt = rec.lead_days
            else:
                rec.dlt = rec.product_id.seller_ids and \
                    rec.product_id.seller_ids[0].delay or rec.lead_days

    buffer_profile_id = fields.Many2one(
        comodel_name='stock.buffer.profile',
        string="Buffer Profile",
    )
    replenish_method = fields.Selection(
        related="buffer_profile_id.replenish_method",
        readonly=True,
    )
    green_override = fields.Float(
        string="Green Zone (Override)",
    )
    yellow_override = fields.Float(
        string="Yellow Zone (Override)",
    )
    red_override = fields.Float(
        string="Red Zone (Override)",
    )
    dlt = fields.Float(string="Decoupled Lead Time (days)",
                       compute="_compute_dlt")
    adu = fields.Float(string="Average Daily Usage (ADU)",
                       default=0.0, digits=UNIT, readonly=True)
    adu_calculation_method = fields.Many2one(
        comodel_name="product.adu.calculation.method",
        string="ADU calculation method")
    adu_fixed = fields.Float(string="Fixed ADU",
                             default=1.0, digits=UNIT)
    order_cycle = fields.Float(string="Minimum Order Cycle (days)")
    minimum_order_quantity = fields.Float(string="Minimum Order Quantity",
                                          digits=UNIT)
    red_base_qty = fields.Float(string="Red Base Qty",
                                compute="_compute_red_zone",
                                digits=UNIT, store=True)
    red_safety_qty = fields.Float(string="Red Safety Qty",
                                  compute="_compute_red_zone",
                                  digits=UNIT, store=True)
    red_zone_qty = fields.Float(string="Red Zone Qty",
                                compute="_compute_red_zone",
                                digits=UNIT, store=True)
    top_of_red = fields.Float(string="Top of Red",
                              related="red_zone_qty", store=True)
    green_zone_qty = fields.Float(string="Green Zone Qty",
                                  compute="_compute_green_zone",
                                  digits=UNIT, store=True)
    green_zone_lt_factor = fields.Float(string="Green Zone Lead Time Factor",
                                        compute="_compute_green_zone",
                                        help="Green zone Lead Time Factor",
                                        store=True)
    green_zone_moq = fields.Float(string="Green Zone Minimum Order Quantity",
                                  compute="_compute_green_zone",
                                  help="Green zone minimum order quantity",
                                  digits=UNIT, store=True)
    green_zone_oc = fields.Float(string="Green Zone Order Cycle",
                                 compute="_compute_green_zone",
                                 help="Green zone order cycle", store=True)
    yellow_zone_qty = fields.Float(string="Yellow Zone Qty",
                                   compute="_compute_yellow_zone",
                                   digits=UNIT, store=True)
    top_of_yellow = fields.Float(string="Top of Yellow",
                                 compute="_compute_yellow_zone",
                                 digits=UNIT, store=True)
    top_of_green = fields.Float(string="Top of Green",
                                compute="_compute_green_zone", digits=UNIT,
                                store=True)
    order_spike_horizon = fields. Float(string="Order Spike Horizon")
    order_spike_threshold = fields.Float(
        string="Order Spike Threshold",
        compute="_compute_order_spike_threshold", digits=UNIT, store=True)
    qualified_demand = fields.Float(string="Qualified demand", digits=UNIT,
                                    readonly=True)
    incoming_dlt_qty = fields.Float(
        string="Incoming (Within DLT)",
        readonly=True,
    )
    net_flow_position = fields.Float(string="Net flow position", digits=UNIT,
                                     readonly=True)
    net_flow_position_percent = fields.Float(
        string="Net flow position (% of TOG)", readonly=True)
    planning_priority_level = fields.Selection(
        string="Planning Priority Level", selection=_PRIORITY_LEVEL,
        readonly=True)
    execution_priority_level = fields.Selection(
        string="On-Hand Alert Level",
        selection=_PRIORITY_LEVEL, store=True, readonly=True)
    on_hand_percent = fields.Float(string="On Hand/TOR (%)",
                                   store=True, readonly=True)
    # We override the calculation method for the procure recommended qty
    procure_recommended_qty = fields.Float(
        compute="_compute_procure_recommended_qty", store=True)
    procure_recommended_date = fields.Date(
        compute="_compute_procure_recommended_date")
    mrp_production_ids = fields.One2many(
        string='Manufacturing Orders', comodel_name='mrp.production',
        inverse_name='orderpoint_id')
    purchase_line_ids = fields.Many2many(comodel_name='purchase.order.line',
                                         string='PO Lines', copy=False)
    ddmrp_chart = fields.Text(string='DDMRP Chart',
                              compute=_compute_ddmrp_chart)

    _order = 'planning_priority_level asc, net_flow_position asc'

    @api.multi
    @api.onchange("red_zone_qty")
    def onchange_red_zone_qty(self):
        for rec in self:
            rec.product_min_qty = rec.red_zone_qty

    @api.multi
    @api.onchange("adu_fixed", "adu_calculation_method")
    def onchange_adu(self):
        self._calc_adu()

    @api.multi
    @api.onchange("top_of_green")
    def onchange_green_zone_qty(self):
        for rec in self:
            rec.product_max_qty = rec.top_of_green

    @api.multi
    def _search_open_stock_moves_domain(self):
        self.ensure_one()
        return [('product_id', '=', self.product_id.id),
                ('state', 'in', ['draft', 'waiting', 'confirmed',
                                 'assigned']),
                ('location_dest_id', '=', self.location_id.id)]

    @api.model
    def _stock_move_tree_view(self, lines):
        views = []
        tree_view = self.env.ref('stock.view_move_tree', False)
        if tree_view:
            views += [(tree_view.id, 'tree')]
        form_view = self.env.ref(
            'stock.view_move_form', False)
        if form_view:
            views += [(form_view.id, 'form')]

        return {
            'name': _('Non-completed Moves'),
            'type': 'ir.actions.act_window',
            'res_model': 'stock.move',
            'view_type': 'form',
            'views': views,
            'view_mode': 'tree,form',
            'domain': str([('id', 'in', lines.ids)]),
        }

    @api.multi
    def open_moves(self):
        self.ensure_one()
        # Utility method used to add an "Open Moves" button in the buffer
        # planning view
        domain = self._search_open_stock_moves_domain()
        records = self.env['stock.move'].search(domain)
        return self._stock_move_tree_view(records)

    @api.multi
    def _past_demand_estimate_domain(self, date_from, date_to, locations):
        self.ensure_one()
        return [('location_id', 'in', locations.ids),
                ('product_id', '=', self.product_id.id),
                ('date_range_id.date_start', '<=', date_to),
                ('date_range_id.date_end', '>=', date_from)]

    @api.multi
    def _past_moves_domain(self, date_from, locations):
        self.ensure_one()
        return [('state', '=', 'done'), ('location_id', 'in', locations.ids),
                ('location_dest_id', 'not in', locations.ids),
                ('product_id', '=', self.product_id.id),
                ('date', '>=', date_from)]

    @api.multi
    def _calc_adu_past_demand(self):
        self.ensure_one()
        horizon = self.adu_calculation_method.horizon or 0
        if self.warehouse_id.calendar_id:
            dt_from = self.warehouse_id.calendar_id.plan_days(
                -1 * horizon - 1, datetime.now())
            date_from = fields.Date.to_string(dt_from)
        else:
            date_from = fields.Date.to_string(
                fields.date.today() - timedelta(days=horizon))
        date_to = fields.Date.today()
        locations = self.env['stock.location'].search(
            [('id', 'child_of', [self.location_id.id])])
        if self.adu_calculation_method.use_estimates:
            qty = 0.0
            domain = self._past_demand_estimate_domain(date_from, date_to,
                                                       locations)
            for estimate in self.env['stock.demand.estimate'].search(domain):
                qty += estimate.get_quantity_by_date_range(
                    fields.Date.from_string(date_from),
                    fields.Date.from_string(date_to))
            return qty / horizon
        else:
            qty = 0.0
            domain = self._past_moves_domain(date_from, locations)
            for group in self.env['stock.move'].read_group(
                    domain, ['product_id', 'product_qty'], ['product_id']):
                qty += group['product_qty']
            return qty / horizon

    @api.multi
    def _future_demand_estimate_domain(self, date_from, date_to, locations):
        self.ensure_one()
        return [('location_id', 'in', locations.ids),
                ('product_id', '=', self.product_id.id),
                ('date_range_id.date_start', '<=', date_to),
                ('date_range_id.date_end', '>=', date_from)]

    @api.multi
    def _future_moves_domain(self, date_to, locations):
        self.ensure_one()
        return [('state', 'not in', ['done', 'cancel']),
                ('location_id', 'in', locations.ids),
                ('location_dest_id', 'not in', locations.ids),
                ('product_id', '=', self.product_id.id),
                ('date_expected', '<=', date_to)]

    @api.multi
    def _calc_adu_future_demand(self):
        self.ensure_one()
        horizon = self.adu_calculation_method.horizon or 1
        if self.warehouse_id.calendar_id:
            dt_to = self.warehouse_id.calendar_id.plan_days(
                horizon-1 + 1, datetime.now())
            date_to = fields.Date.to_string(dt_to)
        else:
            date_to = fields.Date.to_string(
                fields.date.today() + timedelta(days=horizon-1))
        date_from = fields.Date.today()
        locations = self.env['stock.location'].search(
            [('id', 'child_of', [self.location_id.id])])
        if self.adu_calculation_method.use_estimates:
            qty = 0.0
            domain = self._future_demand_estimate_domain(date_from, date_to,
                                                         locations)
            for estimate in self.env['stock.demand.estimate'].search(domain):
                qty += estimate.get_quantity_by_date_range(
                    fields.Date.from_string(date_from),
                    fields.Date.from_string(date_to))
            return qty / horizon
        else:
            qty = 0.0
            domain = self._future_moves_domain(date_to, locations)
            for group in self.env['stock.move'].read_group(
                    domain, ['product_id', 'product_qty'], ['product_id']):
                qty += group['product_qty']
            return qty / horizon

    @api.multi
    def _calc_adu(self):
        for orderpoint in self:
            if orderpoint.adu_calculation_method.method == 'fixed':
                orderpoint.adu = orderpoint.adu_fixed
            elif orderpoint.adu_calculation_method.method == 'past':
                orderpoint.adu = orderpoint._calc_adu_past_demand()
            elif orderpoint.adu_calculation_method.method == 'future':
                orderpoint.adu = orderpoint._calc_adu_future_demand()
        return True

    @api.multi
    def _search_stock_moves_qualified_demand_domain(self):
        self.ensure_one()
        horizon = self.order_spike_horizon
        if self.warehouse_id.calendar_id:
            dt_to = self.warehouse_id.calendar_id.plan_days(
                horizon + 1, datetime.now())
            date_to = fields.Date.to_string(dt_to)
        else:
            date_to = fields.Date.to_string(fields.date.today() +
                                            timedelta(days=horizon))
        locations = self.env['stock.location'].search(
            [('id', 'child_of', [self.location_id.id])])
        return [('product_id', '=', self.product_id.id),
                ('state', 'in', ['waiting', 'confirmed', 'assigned']),
                ('location_id', 'in', locations.ids),
                ('location_dest_id', 'not in', locations.ids),
                ('date_expected', '<=', date_to)]

    @api.multi
    def _search_stock_moves_incoming_domain(self):
        self.ensure_one()
        # We introduce a safety factor of 2 for incoming moves
        factor = self.warehouse_id.nfp_incoming_safety_factor or 1
        horizon = int(self.dlt) * factor
        # For purchased products we use calendar days, not work days
        if self.warehouse_id.calendar_id and \
                self.buffer_profile_id.item_type != 'purchased':
            dt_to = self.warehouse_id.calendar_id.plan_days(
                horizon + 1, datetime.now())
            date_to = fields.Date.to_string(dt_to)
        else:
            date_to = fields.Date.to_string(fields.date.today() +
                                            timedelta(days=horizon))
        locations = self.env['stock.location'].search(
            [('id', 'child_of', [self.location_id.id])])
        return [('product_id', '=', self.product_id.id),
                ('state', 'in', ['waiting', 'confirmed', 'assigned']),
                ('location_id', 'not in', locations.ids),
                ('location_dest_id', 'in', locations.ids),
                ('date_expected', '<=', date_to)]

    @api.multi
    def _calc_qualified_demand(self):
        for rec in self:
            rec.qualified_demand = 0.0
            domain = rec._search_stock_moves_qualified_demand_domain()
            moves = self.env['stock.move'].search(domain)
            demand_by_days = {}
            move_dates = [fields.Datetime.from_string(dt).date() for dt in
                          moves.mapped('date_expected')]
            for move_date in move_dates:
                demand_by_days[move_date] = 0.0
            for move in moves:
                date = fields.Datetime.from_string(move.date_expected).date()
                demand_by_days[date] += \
                    move.product_qty - move.reserved_availability
            for date in demand_by_days:
                if demand_by_days[date] >= rec.order_spike_threshold \
                        or date <= fields.date.today():
                    rec.qualified_demand += demand_by_days[date]
        return True

    @api.multi
    def _calc_incoming_dlt_qty(self):
        for rec in self:
            rec.incoming_dlt_qty = 0.0
            domain = rec._search_stock_moves_incoming_domain()
            moves = self.env['stock.move'].search(domain)
            rec.incoming_dlt_qty = sum(moves.mapped('product_qty'))
        return True

    @api.multi
    def _calc_net_flow_position(self):
        for rec in self:
            rec.net_flow_position = \
                rec.product_location_qty_available_not_res + \
                rec.incoming_dlt_qty - rec.qualified_demand
            usage = 0.0
            if rec.top_of_green:
                usage = round((rec.net_flow_position /
                              rec.top_of_green*100), 2)
            rec.net_flow_position_percent = usage
        return True

    @api.multi
    def _calc_planning_priority(self):
        for rec in self:
            if rec.net_flow_position >= rec.top_of_yellow:
                rec.planning_priority_level = '3_green'
            elif rec.net_flow_position >= rec.top_of_red:
                rec.planning_priority_level = '2_yellow'
            else:
                rec.planning_priority_level = '1_red'

    @api.multi
    def _calc_execution_priority(self):
        for rec in self:
            if rec.product_location_qty_available_not_res >= rec.top_of_red:
                rec.execution_priority_level = '3_green'
            elif rec.product_location_qty_available_not_res >= \
                    rec.top_of_red*0.5:
                rec.execution_priority_level = '2_yellow'
            else:
                rec.execution_priority_level = '1_red'
            if rec.top_of_red:
                rec.on_hand_percent = round((
                    (rec.product_location_qty_available_not_res /
                     rec.top_of_red)*100), 2)
            else:
                rec.on_hand_percent = 0.0

    @api.model
    def cron_ddmrp_adu(self, automatic=False):
        """calculate ADU for each DDMRP buffer. Called by cronjob.
        """
        _logger.info("Start cron_ddmrp_adu.")
        orderpoints = self.search([])
        i = 0
        j = len(orderpoints)
        for op in orderpoints:
            try:
                i += 1
                _logger.debug("ddmrp cron_adu: %s. (%s/%s)" % (op.name, i, j))
                if automatic:
                    with self.env.cr.savepoint():
                        op._calc_adu()
                else:
                    op._calc_adu()
            except Exception:
                _logger.exception(
                    'Fail to compute ADU for orderpoint %s', op.name)
                if not automatic:
                    raise
        _logger.info("End cron_ddmrp_adu.")
        return True

    @api.multi
    def cron_actions(self):
        """This method is meant to be inherited by other modules in order to
        enhance extensibility."""
        self.ensure_one()
        self._calc_qualified_demand()
        self._calc_incoming_dlt_qty()
        self._calc_net_flow_position()
        self._calc_planning_priority()
        self._calc_execution_priority()
        self.mrp_production_ids._calc_execution_priority()
        self.mapped("purchase_line_ids")._calc_execution_priority()
        # FIXME: temporary patch to force the recalculation of zones.
        self._compute_red_zone()
        self._compute_yellow_zone()
        self._compute_green_zone()
        return True

    @api.model
    def cron_ddmrp(self, automatic=False):
        """calculate key DDMRP parameters for each orderpoint
        Called by cronjob.
        """
        _logger.info("Start cron_ddmrp.")
        orderpoints = self.search([])
        i = 0
        j = len(orderpoints)
        orderpoints.refresh()
        for op in orderpoints:
            i += 1
            _logger.debug("ddmrp cron: %s. (%s/%s)" % (op.name, i, j))
            try:
                if automatic:
                    with self.env.cr.savepoint():
                        op.cron_actions()
                else:
                    op.cron_actions()
            except Exception:
                _logger.exception(
                    'Fail to create recurring invoice for orderpoint %s',
                    op.name)
                if not automatic:
                    raise
        _logger.info("End cron_ddmrp.")

        return True
