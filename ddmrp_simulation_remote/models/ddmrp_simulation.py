# Copyright 2020 KMEE
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import locale
import logging
import statistics
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
    (SIMULATION_REMOTE, 'Remote'),
]

ODOO = {}  # Avoid aways reconnect


class DdmrpSimulation(models.Model):
    _inehrit = 'ddmrp.simulation'
    _description = 'DDMRP Simulation'

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

    simulation_type = fields.Selection(
        selection_add=SIMULATION_TYPE,
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
                product_id, simulation_product_external_id, offset + 80
            )

    @job
    def import_product_demand(self, product_id, simulation_product_external_id):
        self.recursive_read_product_demand(
            product_id, simulation_product_external_id
        )

    def button_delete_similation_lines(self):
        for record in self:
            record.simulation_line_ids.unlink()
