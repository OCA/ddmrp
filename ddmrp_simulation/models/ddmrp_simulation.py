# Copyright 2020 KMEE
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import locale
import logging
from datetime import datetime, timedelta

from odoo import api, fields, models, _
from odoo.addons.queue_job.job import job
from odoo.exceptions import AccessDenied, UserError
from odoo.tools.safe_eval import safe_eval

_logger = logging.getLogger(__name__)

try:
    import odoorpc
    import pandas as pd
    import time_machine
except (ImportError, IOError) as err:
    _logger.debug(err)

SIMULATION_REMOTE = 'remote'
SIMULATION_LOCAL = 'local'

SIMULATION_TYPE = [
    (SIMULATION_LOCAL, 'Local'),
    (SIMULATION_REMOTE, 'Remote'),
]

ODOO = {}  # Avoid aways reconnect


class DdmrpSimulation(models.Model):
    _name = 'ddmrp.simulation'
    _description = 'DDMRP Simulation'

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

    @api.depends('remote_address', 'remote_port', 'simulation_type')
    def _compute_database(self):
        for record in self:
            if (record.remote_address and
                record.remote_port and
                    record.simulation_type == SIMULATION_REMOTE):
                try:
                    odoo = record._connection()
                    if odoo:
                        record.remote_database_list = odoo.db.list()
                except Exception as e:
                    raise AccessDenied(
                        _("Error when listing databases {}".format(e))
                    )
            else:
                record.remote_database_list = ''

    @api.depends('product_ids')
    def _compute_imports(self):
        for record in self:
            record.product_imported_count = len(record.product_ids)
            record.in_stock_imported_count = len(record.in_stock_move_ids)
            record.out_stock_imported_count = len(record.out_stock_move_ids)

    name = fields.Char(
        name='Description',
        required=True,
    )
    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('processing', 'Processing'),
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
    )
    remote_address = fields.Char(
        string='Odoo URL',
        help='https://myodoo.oca.org'
    )
    remote_port = fields.Integer(
        string='Odoo Port',
    )
    remote_protocol = fields.Selection(
        string='Protocol',
        selection=[
            ('jsonrpc', 'jsonrpc',),
            ('jsonrpc+ssl', 'jsonrpc+ssl')
        ]
    )
    remote_database_list = fields.Text(
        string='Available databases',
        compute='_compute_database',
    )
    remote_database = fields.Char(
        string='Database',
    )
    remote_user = fields.Char(
        string='User',
    )
    remote_password = fields.Char(
        string='Password',
    )
    connected = fields.Boolean(
        readonly=True
    )
    credentials = fields.Boolean(
        readonly=True
    )
    date_start = fields.Datetime(
        string='Start Date',
        default=fields.Datetime.now,
        required=True
    )
    date_end = fields.Datetime(
        string='End Date',
        readonly=True,
    )
    duration = fields.Float(
        string='Duration',
        compute='_compute_duration',
    )

    #
    #  Product Fields
    #

    product_domain = fields.Text(
        string='Product Domain',
        default="[]"
    )
    product_found_count = fields.Integer(
        string='Product Found',
        readonly=True,
    )
    product_imported_count = fields.Integer(
        string='Product Imported',
        readonly=True,
        compute='_compute_imports'
    )
    product_ids = fields.Many2many(
        'product.product',
        'simulation_product_product_rel',
        'simulation_id',
        'product_id',
        string='Products',
    )

    #
    #  In Stock Fields
    #

    input_stock_date_start = fields.Date(
        string='Stock Move Start'
    )
    input_stock_date_stop = fields.Date(
        string='Stock Move Stop'
    )
    in_stock_domain = fields.Text(
        string='In Stock Domain',
        default="[]"
    )
    in_stock_found_count = fields.Integer(
        string='In Stock Found',
        readonly=True,
    )
    in_stock_imported_count = fields.Integer(
        string='In Stock Imported',
        readonly=True,
        compute='_compute_imports'
    )
    in_stock_move_ids = fields.Many2many(
        'stock.move',
        'simulation_stock_move_in_rel',
        'simulation_id',
        'move_id',
        string='In Stock Moves',
        readonly=True,
    )

    #
    #  Out Stock Fields
    #

    output_stock_date_start = fields.Date(
        string='Stock Move Start'
    )
    output_stock_date_stop = fields.Date(
        string='Stock Move Stop'
    )
    out_stock_domain = fields.Text(
        string='Out Stock Domain',
        default="[]"
    )
    out_stock_found_count = fields.Integer(
        string='Out Stock Found',
        readonly=True,
    )
    out_stock_imported_count = fields.Integer(
        string='Out Stock Imported',
        readonly=True,
        compute='_compute_imports'
    )
    out_stock_move_ids = fields.Many2many(
        'stock.move',
        'simulation_stock_move_out_rel',
        'simulation_id',
        'move_id',
        string='Out Stock Moves',
        readonly=True,
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

    def _connection(self):
        return odoorpc.ODOO(
            host=self.remote_address,
            protocol=self.remote_protocol,
            port=self.remote_port,
            timeout=500,
        )

    def test_connection(self, user_raise=True):
        self.ensure_one()
        try:
            self._connection()
            self.connected = True
        except Exception as e:
            if user_raise:
                raise AccessDenied(
                    _("Connection Error {}".format(e))
                )
            self.connected = False

    def _credentials(self):
        if not ODOO.get(self.id):
            odoo = self._connection()
            odoo.login(self.remote_database, self.remote_user, self.remote_password)
            ODOO[self.id] = odoo
        return ODOO[self.id]

    def _get_env(self):
        if self.simulation_type == SIMULATION_REMOTE:
            return self._credentials().env
        else:
            return self.env

    def _get_record_ids(self, record):
        if self.simulation_type == SIMULATION_REMOTE:
            return record
        else:
            return record.ids

    def test_credentials(self, user_raise=True):
        self.ensure_one()
        try:
            self._credentials()
            self.credentials = True
        except Exception as e:
            if user_raise:
                raise AccessDenied(
                    _("Credentials Error {}".format(e))
                )
            self.credentials = False

    #
    #  Products
    #

    def button_search_product(self):
        for record in self:
            env = self._get_env()
            record.product_found_count = env['product.product'].search_count(
                safe_eval(record.product_domain)
            )

    def button_import_product(self):
        for record in self:
            env = self._get_env()
            products = env['product.product'].search(
                safe_eval(record.product_domain)
            )
        for product in self._get_record_ids(products):
            self.with_delay().import_product_batch(product)

    @job
    def import_product_batch(self, product_id):
        field_list = []
        product_product = self.env['product.product']

        for field in product_product.fields_get_keys():
            if (product_product._fields[field].type not in ('binary', 'image') and
                    not product_product._fields[field].relational):
                field_list.append(
                    product_product._fields[field].name
                )

        result = self._credentials().execute_kw(
            'product.product', 'read',
            args=[product_id],
            kwargs={
                'fields': field_list,
            }
        )[0]

        external_id = 'ddmrp_simulation.{}_{}'.format(
            self.id,
            result['id']
        )
        result['simulation_id'] = self.id
        result['simulation_product_external_id'] = result['id']
        result.pop('id')
        product_product = product_product.create(
            result
        )
        data_list = [{
            'xml_id': external_id,
            'record': product_product,
            'noupdate': True,
        }]
        self.env['ir.model.data']._update_xmlids(data_list)

        if product_product:
            self.simulation_product_ids.create({
                'simulation_id': self.id,
                'product_id': product_product.id,
            })
            self.write({'product_ids': [(4, product_product.id)]})

    def button_delete_products(self):
        for record in self:
            record.product_ids.unlink()

    #
    #  In Stock Moves
    #

    def get_stock_in_domain(self):
        env = self._get_env()
        products = env['product.template'].search(
            safe_eval(self.product_domain)
        )
        domain = safe_eval(self.in_stock_domain)
        domain += [
            ('date', '>=', '2020-08-01'),
            ('date', '<=', '2020-08-31'),
            ('location_id.usage', '=', 'supplier'),
            ('product_id.product_tmpl_id', 'in', self._get_record_ids(products))
        ]
        return domain

    def button_search_in_moves(self):
        for record in self:
            env = self._get_env()
            record.in_stock_found_count = env['stock.move'].search_count(
                self.get_stock_in_domain()
            )

    def button_import_in_moves(self):
        for record in self:
            env = self._get_env()
            moves = env['stock.move'].search(record.get_stock_in_domain(), limit=10)
            for move in self._get_record_ids(moves):
                self.with_delay().import_move_batch(move, move_type='in')

    def button_delete_in_moves(self):
        for record in self:
            record.in_stock_move_ids.unlink()

    def get_stock_out_domain(self):
        env = self._get_env()
        products = env['product.template'].search(
            safe_eval(self.product_domain)
        )
        domain = safe_eval(self.in_stock_domain)
        domain += [
            ('date', '>=', '2020-01-01'),
            ('date', '<=', '2020-08-31'),
            ('location_dest_id.usage', '=', 'customers'),
            ('product_id.product_tmpl_id', 'in', self._get_record_ids(products))
        ]
        return domain

    def button_search_out_moves(self):
        for record in self:
            env = self._get_env()
            record.out_stock_found_count = env['stock.move'].search_count(
                self.get_stock_out_domain()
            )

    def button_import_out_moves(self):
        for record in self:
            env = self._get_env()
            moves = env['stock.move'].search(record.get_stock_out_domain())
            for move in self._get_record_ids(moves):
                self.with_delay().import_move_batch(move, move_type='out')

    def button_delete_out_moves(self):
        for record in self:
            record.out_stock_move_ids.unlink()
    @job
    def import_move_batch(self, move_id, move_type):
        field_list = []
        stock_move = self.env['stock.move']
        env = self._get_env()

        for field in stock_move.fields_get_keys():
            if (stock_move._fields[field].type not in ('binary', 'image') and
                    not stock_move._fields[field].relational):
                field_list.append(
                    stock_move._fields[field].name
                )

        for move in env['stock.move'].browse(move_id):
            result = move.read(field_list)[0]
            external_id = 'ddmrp_simulation.{}_{}'.format(
                self.id,
                result['id']
            )
            result.pop('id')
            stock_move = stock_move.create(
                result
            )
            data_list = [{
                'xml_id': external_id,
                'record': stock_move,
                'noupdate': True,
            }]
            self.env['ir.model.data']._update_xmlids(data_list)
        if stock_move and move_type == 'in':
            self.write({'in_stock_move_ids': [(4, stock_move.id)]})
        elif stock_move and move_type == 'out':
            self.write({'out_stock_move_ids': [(4, stock_move.id)]})

    def button_import_lines(self):
        for record in self:
            range = pd.date_range(start="2020-01-01", end="2020-08-31")
            for i in range:
                date = fields.Datetime.to_string(i)
                record.with_delay().import_product_qty_avaliable(date)

    @job
    def import_product_qty_avaliable(self, date):
        simulation_product_external_id = self.product_ids.mapped(
            'simulation_product_external_id')
        ctx = self.env.context.copy()
        ctx['to_date'] = date
        result = self._credentials().execute_kw(
            'product.product', 'read',
            args=[simulation_product_external_id],
            kwargs={
                'fields': ['qty_available'],
                'context': ctx
            }
        )
        result_dict = {}
        for item in result:
            result_dict[item['id']] = item['qty_available']

        simulation_lines = [
            (4, 0, {})
        ]

        for product in self.product_ids:
            simulation_lines.append((0, 0, {
                'simulation_id': self.id,
                'product_id': product.id,
                'date': date[:10],
                'on_hand': result_dict[product.simulation_product_external_id],
            }))
        self.write({'simulation_line_ids': simulation_lines})

    def button_import_demand(self):
        for record in self:
            for product in record.product_ids:
                record.with_delay().import_product_demand(
                    product.id,
                    product.simulation_product_external_id
                )

    @job
    def recursive_read_product_demand(
          self, product_id, simulation_product_external_id, offset=0):
        move_domain = [
            ("product_id", "=", simulation_product_external_id),
            (
                "state", "in",
                ["done"],
            ),
            ("location_id", "=", 38),
            ("location_dest_id", "=", 9),
            ("date", ">=", '2020-01-01 00:00:00'),
            ("date", "<", '2020-08-31 23:59:59'),
        ]
        answer = self._credentials().execute_kw(
            'stock.move.line', 'read_group',
            kwargs={
                'domain': move_domain,
                'fields': ['date', 'qty_done'],
                'groupby': ['date:day'],
                'limit': 80,
                'offset': offset,
             }
        )
        for item in answer:
            lc = locale.setlocale(locale.LC_TIME)
            try:  # TODO: Refactory - Locale - This can be dangerous!
                locale.setlocale(locale.LC_TIME, "C")
                date = datetime.strptime(item['date:day'].lower(), '%d %b %Y')
            finally:
                locale.setlocale(locale.LC_TIME, lc)

            simulation_line_ids = self.simulation_line_ids.search([
                ('product_id', '=', product_id),
                ('simulation_id', '=', self.id),
                ('date', '=', date.date()),
            ])
            if not simulation_line_ids:
                raise UserError(_("Can't find simulation date"))
            simulation_line_ids.write({
                'demand': item['qty_done'] or 0
            })

        if len(answer) == 80:
            self.with_delay().recursive_read_product_demand(
                product_id, simulation_product_external_id, offset+80
            )

    @job
    def import_product_demand(self, product_id, simulation_product_external_id):
        self.recursive_read_product_demand(
            product_id, simulation_product_external_id
        )

    def button_delete_similation_lines(self):
        for record in self:
            record.simulation_line_ids.unlink()

    def button_create_stock_buffers(self):
        for record in self:
            for simulation_product in record.simulation_product_ids:
                if not simulation_product.stock_buffer_id:
                    if not simulation_product.seller_id:

                        partner = self.env['res.partner']
                        seller = partner.search(
                            [('name', '=', 'Dummy Seller')]
                        )
                        if not seller:
                            seller = partner.create({
                                'name': 'Dummy Seller',
                            })
                        supplierinfo = simulation_product.seller_id.create({
                                'product_id': simulation_product.product_id.id,
                                'product_tmpl_id':
                                simulation_product.product_tmpl_id.id,
                                'name': seller.id,
                            })
                        simulation_product.seller_id = supplierinfo

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
            'picking_type_id':  self.env.ref('stock.picking_type_out').id,
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

    def run_simulation(self):
        for record in self:
            record._simulation_clean()
            start_date = min(record.simulation_line_ids.mapped('date'))
            end_date = max(record.simulation_line_ids.mapped('date'))
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
