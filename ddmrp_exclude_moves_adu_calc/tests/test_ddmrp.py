# Copyright 2016-18 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# Copyright 2016 Aleph Objects, Inc. (https://www.alephobjects.com/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import odoo.tests.common as common
from datetime import datetime, timedelta


class TestDdmrp(common.TransactionCase):

    def setUp(self):
        super(TestDdmrp, self).setUp()

        # Models
        self.productModel = self.env['product.product']
        self.orderpointModel = self.env['stock.warehouse.orderpoint']
        self.pickingModel = self.env['stock.picking']
        self.quantModel = self.env['stock.quant']
        self.aducalcmethodModel = self.env['product.adu.calculation.method']
        self.locationModel = self.env['stock.location']
        self.make_procurement_orderpoint_model =\
            self.env['make.procurement.orderpoint']
        self.user_model = self.env['res.users']

        # Refs
        self.main_company = self.env.ref('base.main_company')
        self.warehouse = self.env.ref('stock.warehouse0')
        self.stock_location = self.env.ref('stock.stock_location_stock')
        self.location_shelf1 = self.env.ref('stock.stock_location_components')
        self.supplier_location = self.env.ref('stock.stock_location_suppliers')
        self.customer_location = self.env.ref('stock.stock_location_customers')
        self.uom_unit = self.env.ref('product.product_uom_unit')
        self.buffer_profile_pur = self.env.ref(
            'ddmrp.stock_buffer_profile_replenish_purchased_short_low')
        self.group_stock_manager = self.env.ref('stock.group_stock_manager')

        # Create users
        self.user = self._create_user('user_1',
                                      [self.group_stock_manager])

        self.productA = self.productModel.create(
            {'name': 'product A',
             'standard_price': 1,
             'type': 'product',
             'uom_id': self.uom_unit.id,
             'default_code': 'A',
             })

        self.inventory_loc = self.locationModel.create({
            'usage': 'inventory',
            'name': 'Inventory',
            'company_id': self.main_company.id
        })

        self.binA = self.locationModel.create({
            'usage': 'internal',
            'name': 'Bin A',
            'location_id': self.location_shelf1.id,
            'company_id': self.main_company.id
        })

        self.binB = self.locationModel.create({
            'usage': 'internal',
            'name': 'Bin B',
            'location_id': self.location_shelf1.id,
            'company_id': self.main_company.id
        })

        self.locationModel._parent_store_compute()

        self.quant = self.quantModel.create(
            {'location_id': self.binA.id,
             'company_id': self.main_company.id,
             'product_id': self.productA.id,
             'quantity': 200.0})

    def _create_user(self, login, groups):
        """ Create a user."""
        group_ids = [group.id for group in groups]
        user = \
            self.user_model.with_context({'no_reset_password': True}).create({
                'name': 'Test User',
                'login': login,
                'password': 'demo',
                'email': 'test@yourcompany.com',
                'groups_id': [(6, 0, group_ids)]
            })
        return user

    def create_pickingoutA(self, date_move, qty):
        return self.pickingModel.sudo(self.user).create({
            'picking_type_id': self.ref('stock.picking_type_out'),
            'location_id': self.binA.id,
            'location_dest_id': self.customer_location.id,
            'move_lines': [
                (0, 0, {
                    'name': 'Test move',
                    'product_id': self.productA.id,
                    'date_expected': date_move,
                    'date': date_move,
                    'product_uom': self.productA.uom_id.id,
                    'product_uom_qty': qty,
                    'location_id': self.binA.id,
                    'location_dest_id': self.customer_location.id,
                })]
        })

    def create_pickingoutB(self, date_move, qty):
        return self.pickingModel.sudo(self.user).create({
            'picking_type_id': self.ref('stock.picking_type_out'),
            'location_id': self.binA.id,
            'location_dest_id': self.inventory_loc.id,
            'move_lines': [
                (0, 0, {
                    'name': 'Test move',
                    'product_id': self.productA.id,
                    'date_expected': date_move,
                    'date': date_move,
                    'product_uom': self.productA.uom_id.id,
                    'product_uom_qty': qty,
                    'location_id': self.binA.id,
                    'location_dest_id': self.customer_location.id,
                })]
        })

    def test_01_exclude_move_from_adu(self):

        method = self.env.ref('ddmrp.adu_calculation_method_past_120')
        orderpointA = self.orderpointModel.create({
            'buffer_profile_id': self.buffer_profile_pur.id,
            'product_id': self.productA.id,
            'location_id': self.stock_location.id,
            'warehouse_id': self.warehouse.id,
            'product_min_qty': 0.0,
            'product_max_qty': 0.0,
            'qty_multiple': 0.0,
            'dlt': 10,
            'adu_calculation_method': method.id,
            'adu_fixed': 4
        })
        self.orderpointModel.cron_ddmrp_adu()

        self.assertEqual(orderpointA.adu, 0)

        pickingOuts = self.pickingModel
        date_move = datetime.today() - timedelta(days=30)
        pickingOut = self.create_pickingoutA(date_move, 60)
        for move in pickingOut.move_lines:
            move.exclude_from_adu = True
        pickingOuts += pickingOut
        date_move = datetime.today() - timedelta(days=60)
        pickingOuts += self.create_pickingoutA(date_move, 60)
        pickingOuts += self.create_pickingoutB(date_move, 60)
        for picking in pickingOuts:
            picking.action_confirm()
            picking.action_assign()
            for line in picking.move_line_ids:
                line.qty_done = 60
            picking.action_done()

        self.orderpointModel.cron_ddmrp_adu()
        to_assert_value = (60 + 60) / 120
        self.assertEqual(orderpointA.adu, to_assert_value)
