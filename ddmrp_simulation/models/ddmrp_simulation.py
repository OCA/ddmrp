# Copyright 2020 KMEE
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import io
import base64
import logging
import statistics
import xlrd
from datetime import timedelta
from odoo.modules.module import get_resource_path
from odoo.exceptions import UserError

from odoo import api, fields, models, tools, _

_logger = logging.getLogger(__name__)

try:
    import odoorpc
    import pandas as pd
    import time_machine
except (ImportError, IOError) as err:
    _logger.debug(err)

SIMULATION_LOCAL = 'local'
SIMULATION_FILE = 'file'

SIMULATION_TYPE = [
    (SIMULATION_LOCAL, 'Local'),
    (SIMULATION_FILE, 'File'),
]


class DdmrpSimulation(models.Model):
    _name = 'ddmrp.simulation'
    _description = 'DDMRP Simulation'

    def _default_simulation_file(self):
        file_path = get_resource_path(
            'ddmrp_simulation', 'static/xlsx', 'OdooSimulationTemplate.xlsx')
        with tools.file_open(file_path, 'rb') as f:
            return base64.b64encode(f.read())

    @api.depends('date_end', 'date_start')
    def _compute_duration(self):
        for record in self:
            if record.date_end:
                d1 = fields.Datetime.from_string(record.date_start)
                d2 = fields.Datetime.from_string(record.date_end)
                diff = d2 - d1
                record.duration = round(diff.total_seconds() / 60.0, 2)
            else:
                record.duration = 0.0

    name = fields.Char(
        name='Description',
        required=True,
        copy=False,
        default=lambda self: self.env['ir.sequence'].next_by_code('ddmrp.simulation')
    )
    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('imported', 'Data Imported'),
            ('processing', 'Processing'),
            ('ready', 'Ready'),
            ('done', 'Done'),
        ],
        name='State',
        default='draft',
        required=True,
        readonly=True,
    )
    simulation_type = fields.Selection(
        selection=SIMULATION_TYPE,
        name='Simulation Type',
        required=True,
        default=SIMULATION_FILE,
    )
    date_start = fields.Datetime(
        string='Start Date',
        readonly=True,
    )
    date_end = fields.Datetime(
        string='End Date',
        readonly=True,
    )
    duration = fields.Float(
        string='Duration',
        compute='_compute_duration',
    )
    simulation_date_start = fields.Date(
        string='Start Date',
        readonly=True,
    )
    simulation_date_end = fields.Date(
        string='End Date',
        readonly=True,
    )
    simulation_date_current = fields.Date(
        string='Current Date',
        readonly=True,
    )
    simulation_step = fields.Integer(default=1)

    product_ids = fields.Many2many(
        'product.product',
        'simulation_product_product_rel',
        'simulation_id',
        'product_id',
        string='Products',
    )

    simulation_product_ids = fields.One2many(
        comodel_name='ddmrp.simulation.product',
        inverse_name='simulation_id',
    )
    simulation_line_ids = fields.One2many(
        comodel_name='ddmrp.simulation.line',
        inverse_name='simulation_id',
    )
    stock_buffers_ids = fields.One2many(
        'stock.buffer',
        'simulation_id',
        string='Stock Buffers',
    )
    initial_inventory_id = fields.Many2one(
        comodel_name='stock.inventory',
        string='Initial Inventory',
    )
    result_ids = fields.One2many(
        comodel_name='ddmrp.simulation.total.result',
        inverse_name='simulation_id',
        string='Results'
    )
    simulation_file_name = fields.Char(
        string='File Name',
        default='OdooSimulationTemplate.xlsx'
    )
    simulation_file = fields.Binary(
        string='Simulation File',
        default=_default_simulation_file,
    )

    def _create_stock_buffers(self):
        for record in self:
            for simulation_product in record.simulation_product_ids:
                if not simulation_product.stock_buffer_id:

                    buffer_profile = self.env['stock.buffer.profile'].search([
                        ('replenish_method', '=', simulation_product.replenish_method),
                        ('item_type', '=', simulation_product.item_type),
                        ('lead_time_id', '=', simulation_product.lead_time_id.id),
                        ('variability_id', '=', simulation_product.variability_id.id),
                    ], limit=1)

                    if buffer_profile:
                        simulation_product.stock_buffer_id = \
                            simulation_product.stock_buffer_id.create({
                                'product_id': simulation_product.product_id.id,
                                'buffer_profile_id': buffer_profile.id,
                                'adu_calculation_method':
                                    simulation_product.adu_calculation_method.id,
                                'simulation_id': self.id,
                                'order_spike_horizon': 7,
                                'auto_procure': True,
                                'auto_procure_option': 'standard',
                            })

    def _simulation_create_initial_inventory(self):
        if not self.initial_inventory_id:
            line_ids = [(6, 0, {})]

            inventory_vals = {
                "name": "Initial Inventory / Simulation ID: {} NAME: {}".format(
                    self.id, self.name),
                "prefill_counted_quantity": 'zero',
                "product_ids": [(6, 0, self.product_ids.ids)],
                "location_ids": [
                    (6, 0, [self.env.ref('stock.stock_location_stock').id])],
                "line_ids": line_ids,
            }

            for product_id in self.product_ids:
                simulation_line = self.simulation_line_ids.search([
                    ('simulation_id', '=', self.id),
                    ('product_id', '=', product_id.id),
                    ('date', '=', fields.Date.today()),
                ])
                on_hand = simulation_line.on_hand
                if on_hand < 0:
                    on_hand = 0
                line_ids.append((0, 0, {
                    'product_id': product_id.id,
                    'product_qty': on_hand,
                    'product_uom_id': product_id.uom_id.id,
                    'location_id': self.env.ref('stock.stock_location_stock').id,
                }))

            self.initial_inventory_id = self.env['stock.inventory'].create(
                inventory_vals
            )
            self.initial_inventory_id.action_start()
            self.initial_inventory_id.action_validate()

    def _simulation_create_out_demand(self):
        simulation_lines = self.simulation_line_ids.search([
            ('simulation_id', '=', self.id),
            ('product_id', 'in', self.product_ids.ids),
            ('date', '=', fields.Date.today()),
        ])
        move_lines = [(6, 0, {})]
        picking_vals = {
            'picking_type_id': self.env.ref('stock.picking_type_out').id,
            'location_id': self.env.ref('stock.stock_location_stock').id,
            'location_dest_id': self.env.ref('stock.stock_location_customers').id,
            'scheduled_date': fields.Datetime.now(),
            'move_lines': move_lines,
        }

        for line in simulation_lines:
            move_lines.append((0, 0, {
                'name': line.product_id.name,
                'product_id': line.product_id.id,
                'product_uom': line.product_id.uom_id.id,
                'product_uom_qty': line.demand,
                'quantity_done': line.demand,
                'location_id': self.env.ref('stock.stock_location_stock').id,
                'location_dest_id': self.env.ref('stock.stock_location_customers').id,
                'date': fields.Datetime.now(),
            }))

        picking_id = self.env['stock.picking'].create(picking_vals)
        picking_id.action_done()

    def _simulation_confirm_po(self):
        po_ids = self.stock_buffers_ids.mapped('purchase_line_ids').mapped('order_id')
        po_ids.button_confirm()

    def _simulation_confirm_receive(self):
        end_of_today = fields.Date.today() + timedelta(days=1)
        picking_ids = self.env['stock.picking'].search([
            ('scheduled_date', '<', end_of_today),
            ('state', '!=', 'done')
        ])
        if picking_ids:
            picking_ids.action_confirm()
            self.env['stock.immediate.transfer'].create(
                {'pick_ids': [(6, 0, picking_ids.ids)]}).process()

    def _simulation_clean(self):
        self.env.cr.execute("""
           delete from stock_move_line;
           delete from stock_move;
           delete from stock_picking;
           delete from stock_inventory_line;
           delete from stock_inventory;
           delete from stock_valuation_layer;
           delete from stock_quant;
           delete from ddmrp_history;
           delete from purchase_order;
           delete from purchase_order_line;
        """)
        self._cr.commit()

    def action_run_simulation(self):
        for record in self:
            if not record.env.context.get('step'):
                record._simulation_clean()
                start_date = record.simulation_date_start
                end_date = record.simulation_date_end
            else:
                if record.simulation_date_current:
                    start_date = record.simulation_date_current + timedelta(days=1)
                else:
                    start_date = record.simulation_date_start
                end_date = start_date + timedelta(days=record.step)
            if not record.date_start:
                record.date_start = fields.Datetime.now()

            range = pd.date_range(start=start_date, end=end_date)
            for simulation_day in range:
                # Criar inventário na data
                # Criar vendas

                traveller = time_machine.travel(simulation_day)
                traveller.start()
                if simulation_day == start_date:
                    record._simulation_create_initial_inventory()
                record._simulation_confirm_receive()
                self.env['stock.buffer'].cron_ddmrp(True)
                record._simulation_create_out_demand()
                self.env['stock.buffer'].cron_ddmrp_adu(True)
                self.env['stock.buffer'].cron_ddmrp(True)
                record._simulation_confirm_po()
                self._cr.commit()
                traveller.stop()

            if simulation_day == record.simulation_date_end:
                record.state = 'ready'
                record.date_end = fields.Datetime.now()
            else:
                record.state = 'processing'
                record.simulation_date_current = simulation_day

    def action_view_related_products(self):
        self.ensure_one()
        domain = [('id', 'in', self.product_ids.ids)]
        action = {
            'name': _('Product of the Simulation'),
            'type': 'ir.actions.act_window',
            'res_model': 'product.product',
            'view_type': 'list',
            'view_mode': 'list,form',
            'domain': domain,
        }
        return action

    def action_view_related_buffers(self):
        self.ensure_one()
        domain = [('simulation_id', '=', self.id)]
        action = {
            'name': _('Buffers of the Simulation'),
            'type': 'ir.actions.act_window',
            'res_model': 'stock.buffer',
            'view_type': 'list',
            'view_mode': 'list,form',
            'domain': domain,
        }
        return action

    def action_view_related_simulation_lines(self):
        self.ensure_one()
        domain = [('simulation_id', '=', self.id)]
        action = {
            'name': _('Simulation Lines'),
            'type': 'ir.actions.act_window',
            'res_model': 'ddmrp.simulation.product',
            'view_type': 'list',
            'view_mode': 'list,form',
            'domain': domain,
        }
        return action

    def action_compute_results(self):
        for record in self:
            for simulation_product_id in record.simulation_product_ids:
                simulation_product_id.result_ids.unlink()
                simulation_product_id.button_statistics()

            result_ids = record.simulation_product_ids.result_ids
            average_on_hand = result_ids.filtered(
                lambda x: x.code == 'average_on_hand')
            average_on_hand_value = result_ids.filtered(
                lambda x: x.code == 'average_on_hand_value')
            total_demand = result_ids.filtered(lambda x: x.code == 'total_demand')
            turnover = result_ids.filtered(lambda x: x.code == 'turnover')
            peak_demand = result_ids.filtered(lambda x: x.code == 'peak_demand')
            supply_orders = result_ids.filtered(lambda x: x.code == 'supply_orders')
            average_order_size = result_ids.filtered(
                lambda x: x.code == 'average_order_size')
            minimum_on_hand = result_ids.filtered(
                lambda x: x.code == 'minimum_on_hand')
            max_on_hand = result_ids.filtered(lambda x: x.code == 'max_on_hand')
            service_level = result_ids.filtered(lambda x: x.code == 'service_level')
            days_stock_out = result_ids.filtered(lambda x: x.code == 'days_stock_out')

            results = [
                (6, 0, {}),
                (0, 0, {
                    'code': 'average_on_hand',
                    'name': 'Average On Hand - QTY',
                    'current': statistics.mean(average_on_hand.mapped('current')),
                    'simulation':
                        statistics.mean(average_on_hand.mapped('simulation')),
                }),
                (0, 0, {
                    'code': 'average_on_hand_value',
                    'name': 'Average On Hand - Value ($)',
                    'current':
                        statistics.mean(average_on_hand_value.mapped('current')),
                    'simulation':
                        statistics.mean(average_on_hand_value.mapped('simulation')),
                }),
                (0, 0, {
                    'code': 'total_demand',
                    'name': 'Total Demand',
                    'current': statistics.mean(total_demand.mapped('current')),
                    'simulation': statistics.mean(total_demand.mapped('simulation')),
                }),
                (0, 0, {
                    'code': 'turnover',
                    'name': 'Average Turnover',
                    'current': statistics.mean(turnover.mapped('current')),
                    'simulation': statistics.mean(turnover.mapped('simulation')),
                }),
                (0, 0, {
                    'code': 'peak_demand',
                    'name': 'Peak Demand',
                    'current': statistics.mean(peak_demand.mapped('current')),
                    'simulation':
                        statistics.mean(peak_demand.mapped('simulation')),
                }),
                (0, 0, {
                    'code': 'supply_orders',
                    'name': 'Supply Orders',
                    'current': statistics.mean(supply_orders.mapped('current')),
                    'simulation':
                        statistics.mean(supply_orders.mapped('simulation')),
                }),
                (0, 0, {
                    'code': 'average_order_size',
                    'name': 'Average Order Size',
                    'current': statistics.mean(average_order_size.mapped('current')),
                    'simulation':
                        statistics.mean(average_order_size.mapped('simulation')),
                }),
                (0, 0, {
                    'code': 'minimum_on_hand',
                    'name': 'Minimum On Hand',
                    'current': statistics.mean(minimum_on_hand.mapped('current')),
                    'simulation':
                        statistics.mean(minimum_on_hand.mapped('simulation')),
                }),
                (0, 0, {
                    'code': 'max_on_hand',
                    'name': 'Max On Hand',
                    'current': statistics.mean(max_on_hand.mapped('current')),
                    'simulation': statistics.mean(max_on_hand.mapped('simulation')),
                }),
                (0, 0, {
                    'code': '',
                    'name': 'Service Level',
                    'current': statistics.mean(service_level.mapped('current')),
                    'simulation':
                        statistics.mean(service_level.mapped('simulation')),
                }),
                (0, 0, {
                    'code': 'days_stock_out',
                    'name': 'Days Stock Out',
                    'current': statistics.mean(days_stock_out.mapped('current')),
                    'simulation':
                        statistics.mean(days_stock_out.mapped('simulation')),
                }),
            ]

            record.write({
                'result_ids': results,
            })

    def _import_file_forecast(self, data):
        pass

    def _import_file_historical_stock(self, data):
        data = data.set_index(["Part number", 'Date'])
        for index, row in data.iterrows():
            product_id = self.env['product.product'].search([
                ('default_code', '=', index[0])
            ])
            if not product_id:
                raise UserError(
                    _('Part number not found when processing sheet Historical Stock'))

            simulation_line_id = self.simulation_line_ids.search([
                ('simulation_id', '=', self.id),
                ('product_id', '=', product_id.id),
                ('date', '=', index[1].date()),
            ])
            if simulation_line_id:
                simulation_line_id.on_hand = row['Qty']
            else:
                self.simulation_line_ids.create({
                    'simulation_id': self.id,
                    'product_id': product_id.id,
                    'date': index[1].date(),
                    'on_hand': row['Qty'],
                })

    def _import_file_demand_history(self, data):
        data = data.set_index(["Part number", 'Date consumed'])
        for index, row in data.iterrows():
            product_id = self.env['product.product'].search([
                ('default_code', '=', index[0])
            ])
            if not product_id:
                raise UserError(
                    _('Part number not found when processing sheet Demand History'))

            self.simulation_line_ids.create({
                'simulation_id': self.id,
                'product_id': product_id.id,
                'date': index[1].date(),
                'demand': row['Qty'],
            })

    def _import_file_bill_of_material(self, data):
        pass

    def _create_simulation_product(self, product_id):
        self.write({
            'product_ids': [(4, product_id.id)],
            'simulation_product_ids': [(0, 0, {
                'simulation_id': self.id,
                'product_id': product_id.id,
                'seller_id': product_id.seller_ids[0].id
            })]
        })

    def _create_product_product(self, default_code, name, seller_id=False,
                                leadtime=False, moq=False, price=0):
        product_id = self.env['product.product']
        product_id = product_id.search([
            ('default_code', '=', default_code),
        ])
        if not product_id:
            product_vals = {
                'name': name,
                'default_code': default_code,
                'type': 'product',
                'standard_price': price,
            }
            if seller_id:
                product_vals['seller_ids'] = [
                    (6, 0, {}),
                    (0, 0, {
                        'name': seller_id.id,
                        'delay': leadtime,
                        'min_qty': moq,
                        'price': price,
                    })
                ]
            product_id = product_id.create(product_vals)
        return product_id

    def _create_supplier(self, name):
        partner_id = self.env['res.partner']
        partner_id = partner_id.search([
            ('name', '=', name),
        ])
        if not partner_id:
            partner_id = partner_id.create({
                'name': name,
            })
        return partner_id

    def _import_file_master_data(self, data):
        data = data.set_index(["Part number"])
        for index, row in data.iterrows():
            supplier_id = self._create_supplier(name=row['Supplier'])
            product_id = self._create_product_product(
                default_code=index,
                name=row['Part Name'],
                seller_id=supplier_id,
                leadtime=row['Leadtime'],
                moq=row['Minimum order quantity'],
                price=row['Material cost'],
            )
            self._create_simulation_product(product_id)

    def _import_file(self):
        for record in self:
            if not record.simulation_file:
                raise UserError(_(
                    "Please insert a file to start the simulation",
                ))
            record.simulation_product_ids.unlink()
            record.simulation_line_ids.unlink()

            inputx = io.BytesIO(base64.decodebytes(record.simulation_file))
            record._import_file_master_data(
                pd.read_excel(inputx.getvalue(), sheet_name='MasterData'))
            record._import_file_bill_of_material(
                pd.read_excel(inputx.getvalue(), sheet_name='BillOfMaterial'))
            record._import_file_demand_history(
                pd.read_excel(inputx.getvalue(), sheet_name='DemandHistory'))
            record._import_file_historical_stock(
                pd.read_excel(inputx.getvalue(), sheet_name='HistoricalStock'))
            record._import_file_forecast(
                pd.read_excel(inputx.getvalue(), sheet_name='Forecast'))

            record._create_stock_buffers()
            record.simulation_date_start = min(
                record.simulation_line_ids.mapped('date'))
            record.simulation_date_end = max(
                record.simulation_line_ids.mapped('date'))
            record.state = 'imported'

    def import_master_data(self):
        to_import = self.filtered(lambda x: x.simulation_type == 'file')
        if to_import:
            to_import._import_file()

    def action_start_simulation(self):
        for record in self:
            record.import_master_data()
