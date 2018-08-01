# Copyright 2016-18 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# Copyright 2016 Aleph Objects, Inc. (https://www.alephobjects.com/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import odoo.tests.common as common
from odoo import fields
from datetime import datetime, timedelta


class TestDdmrp(common.SavepointCase):

    def createEstimatePeriod(self, name, date_from, date_to):
        date_range_type = self.env['date.range.type'].create({
            'name': 'Test Ranges',
        })
        data = {
            'name': name,
            'date_start': fields.Date.to_string(date_from),
            'date_end': fields.Date.to_string(date_to),
            'type_id': date_range_type.id,
        }
        res = self.estimatePeriodModel.create(data)
        return res

    @classmethod
    def setUpClass(cls):
        super(TestDdmrp, cls).setUpClass()

        # Models
        cls.productModel = cls.env['product.product']
        cls.bomModel = cls.env['mrp.bom']
        cls.orderpointModel = cls.env['stock.warehouse.orderpoint']
        cls.pickingModel = cls.env['stock.picking']
        cls.quantModel = cls.env['stock.quant']
        cls.estimateModel = cls.env['stock.demand.estimate']
        cls.estimatePeriodModel = cls.env['date.range']
        cls.aducalcmethodModel = cls.env['product.adu.calculation.method']
        cls.locationModel = cls.env['stock.location']
        cls.make_procurement_orderpoint_model =\
            cls.env['make.procurement.orderpoint']
        cls.user_model = cls.env['res.users']

        # Refs
        cls.main_company = cls.env.ref('base.main_company')
        cls.warehouse = cls.env.ref('stock.warehouse0')
        cls.stock_location = cls.env.ref('stock.stock_location_stock')
        cls.location_shelf1 = cls.env.ref('stock.stock_location_components')
        cls.supplier_location = cls.env.ref('stock.stock_location_suppliers')
        cls.customer_location = cls.env.ref('stock.stock_location_customers')
        cls.uom_unit = cls.env.ref('product.product_uom_unit')
        cls.buffer_profile_pur = cls.env.ref(
            'ddmrp.stock_buffer_profile_replenish_purchased_medium_medium')
        cls.group_stock_manager = cls.env.ref('stock.group_stock_manager')
        cls.group_mrp_user = cls.env.ref('mrp.group_mrp_user')
        cls.group_change_procure_qty = cls.env.ref(
            'stock_orderpoint_manual_procurement.'
            'group_change_orderpoint_procure_qty')
        cls.calendar = cls.env.ref('resource.resource_calendar_std')

        cls.warehouse.calendar_id = cls.calendar
        # Create users
        cls.user = cls._create_user('user_1',
                                    [cls.group_stock_manager,
                                     cls.group_mrp_user,
                                     cls.group_change_procure_qty])

        manufacture_route = cls.env.ref('mrp.route_warehouse0_manufacture')
        cls.productA = cls.productModel.create(
            {'name': 'product A',
             'standard_price': 1,
             'type': 'product',
             'uom_id': cls.uom_unit.id,
             'default_code': 'A',
             'route_ids': [(6, 0, manufacture_route.ids)]
             })
        cls.bomA = cls.bomModel.create({
            'product_tmpl_id': cls.productA.product_tmpl_id.id,
            'product_id': cls.productA.id,
        })

        cls.binA = cls.locationModel.create({
            'usage': 'internal',
            'name': 'Bin A',
            'location_id': cls.location_shelf1.id,
            'company_id': cls.main_company.id
        })

        cls.binB = cls.locationModel.create({
            'usage': 'internal',
            'name': 'Bin B',
            'location_id': cls.location_shelf1.id,
            'company_id': cls.main_company.id
        })

        cls.locationModel._parent_store_compute()

        cls.quant = cls.quantModel.create(
            {'location_id': cls.binA.id,
             'company_id': cls.main_company.id,
             'product_id': cls.productA.id,
             'quantity': 200.0})

    @classmethod
    def _create_user(cls, login, groups):
        """ Create a user."""
        group_ids = [group.id for group in groups]
        user = \
            cls.user_model.with_context({'no_reset_password': True}).create({
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

    def create_pickinginA(self, date_move, qty):
        return self.pickingModel.sudo(self.user).create({
            'picking_type_id': self.ref('stock.picking_type_in'),
            'location_id': self.supplier_location.id,
            'location_dest_id': self.binA.id,
            'move_lines': [
                (0, 0, {
                    'name': 'Test move',
                    'product_id': self.productA.id,
                    'date_expected': date_move,
                    'date': date_move,
                    'product_uom': self.productA.uom_id.id,
                    'product_uom_qty': qty,
                    'location_id': self.supplier_location.id,
                    'location_dest_id': self.binA.id,
                })]
        })

    def create_pickinginternalA(self, date_move, qty):
        return self.pickingModel.sudo(self.user).create({
            'picking_type_id': self.ref('stock.picking_type_internal'),
            'location_id': self.binA.id,
            'location_dest_id': self.binB.id,
            'move_lines': [
                (0, 0, {
                    'name': 'Test move',
                    'product_id': self.productA.id,
                    'date_expected': date_move,
                    'date': date_move,
                    'product_uom': self.productA.uom_id.id,
                    'product_uom_qty': qty,
                    'location_id': self.binA.id,
                    'location_dest_id': self.binB.id
                })]
        })

    def create_orderpoint_procurement(self, orderpoint):
        """Make Procurement from Reordering Rule"""
        context = {
            'active_model': 'stock.warehouse.orderpoint',
            'active_ids': orderpoint.ids,
            'active_id': orderpoint.id
        }
        wizard = self.make_procurement_orderpoint_model.sudo(self.user).\
            with_context(context).create({})
        wizard.make_procurement()
        return wizard

    def test_adu_calculation_fixed(self):
        method = self.env.ref('ddmrp.adu_calculation_method_fixed')

        orderpointA = self.orderpointModel.create({
            'buffer_profile_id': self.buffer_profile_pur.id,
            'product_id': self.productA.id,
            'location_id': self.stock_location.id,
            'warehouse_id': self.warehouse.id,
            'product_min_qty': 0.0,
            'product_max_qty': 0.0,
            'qty_multiple': 0.0,
            'adu_calculation_method': method.id,
            'adu_fixed': 4
        })
        self.orderpointModel.cron_ddmrp_adu()

        to_assert_value = 4
        self.assertEqual(orderpointA.adu, to_assert_value)

    def test_adu_calculation_past_120_days(self):

        method = self.env.ref('ddmrp.adu_calculation_method_past_120')
        orderpointA = self.orderpointModel.create({
            'buffer_profile_id': self.buffer_profile_pur.id,
            'product_id': self.productA.id,
            'location_id': self.stock_location.id,
            'warehouse_id': self.warehouse.id,
            'product_min_qty': 0.0,
            'product_max_qty': 0.0,
            'qty_multiple': 0.0,
            'adu_calculation_method': method.id,
            'adu_fixed': 4
        })
        self.orderpointModel.cron_ddmrp_adu()

        self.assertEqual(orderpointA.adu, 0)

        pickingOuts = self.pickingModel

        days = 30
        date_move = self.calendar.plan_days(
            -1 * days - 1, datetime.today())
        pickingOuts += self.create_pickingoutA(date_move, 60)
        days = 60
        date_move = self.calendar.plan_days(
            -1 * days - 1, datetime.today())
        pickingOuts += self.create_pickingoutA(date_move, 60)
        for picking in pickingOuts:
            picking.action_confirm()
            picking.force_assign()
            picking.move_lines.quantity_done = 60
            picking.action_done()

        self.orderpointModel.cron_ddmrp_adu()
        to_assert_value = (60 + 60) / 120
        self.assertEqual(orderpointA.adu, to_assert_value)

    def test_adu_calculation_internal_past_120_days(self):
        """
        Test that internal moves will not affect ADU calculation.
        """
        method = self.env.ref('ddmrp.adu_calculation_method_past_120')
        orderpointA = self.orderpointModel.create({
            'buffer_profile_id': self.buffer_profile_pur.id,
            'product_id': self.productA.id,
            'location_id': self.stock_location.id,
            'warehouse_id': self.warehouse.id,
            'product_min_qty': 0.0,
            'product_max_qty': 0.0,
            'qty_multiple': 0.0,
            'adu_calculation_method': method.id,
            'adu_fixed': 4
        })
        self.orderpointModel.cron_ddmrp_adu()

        self.assertEqual(orderpointA.adu, 0)

        pickingInternals = self.pickingModel
        days = 30
        date_move = self.calendar.plan_days(
            -1 * days - 1, datetime.today())
        pickingInternals += self.create_pickinginternalA(date_move, 60)
        days = 60
        date_move = self.calendar.plan_days(
            -1 * days - 1, datetime.today())
        pickingInternals += self.create_pickinginternalA(date_move, 60)
        for picking in pickingInternals:
            picking.action_confirm()
            picking.action_assign()
            picking.action_done()

        self.orderpointModel.cron_ddmrp_adu()

        to_assert_value = 0
        self.assertEqual(orderpointA.adu, to_assert_value)

    def test_adu_calculation_future_120_days_actual(self):
        method = self.aducalcmethodModel.create({
            'name': 'Future actual demand (120 days)',
            'method': 'future',
            'use_estimates': False,
            'horizon': 120,
            'company_id': self.main_company.id
        })

        pickingOuts = self.pickingModel
        days = 30
        date_move = self.calendar.plan_days(
            +1 * days + 1, datetime.today())
        pickingOuts += self.create_pickingoutA(date_move, 60)
        days = 60
        date_move = self.calendar.plan_days(
            +1 * days + 1, datetime.today())
        pickingOuts += self.create_pickingoutA(date_move, 60)

        pickingOuts.action_confirm()

        orderpointA = self.orderpointModel.create({
            'buffer_profile_id': self.buffer_profile_pur.id,
            'product_id': self.productA.id,
            'location_id': self.stock_location.id,
            'warehouse_id': self.warehouse.id,
            'product_min_qty': 0.0,
            'product_max_qty': 0.0,
            'qty_multiple': 0.0,
            'adu_calculation_method': method.id
        })
        self.orderpointModel.cron_ddmrp_adu()

        to_assert_value = (60 + 60) / 120
        self.assertEqual(orderpointA.adu, to_assert_value)

        # Create a move more than 120 days in the future
        days = 150
        date_move = self.calendar.plan_days(
            +1 * days + 1, datetime.today())
        pickingOuts += self.create_pickingoutA(date_move, 1)

        # The extra move should not affect to the average ADU
        self.assertEqual(orderpointA.adu, to_assert_value)

    def test_adu_calculation_future_120_days_estimated(self):

        method = self.env.ref('ddmrp.adu_calculation_method_future_120')
        # Create a period of 120 days.
        date_from = self.calendar.plan_days(1, datetime.today()).date()
        days = 119
        dt = self.calendar.plan_days(
            +1 * days + 1, datetime.today())
        date_to = dt.date()
        estimate_period_next_120 = self.createEstimatePeriod(
            'test_next_120', date_from, date_to)

        self.estimateModel.create({
            'date_range_id': estimate_period_next_120.id,
            'product_id': self.productA.id,
            'product_uom_qty': 120,
            'product_uom': self.productA.uom_id.id,
            'location_id': self.stock_location.id
        })

        orderpointA = self.orderpointModel.create({
            'buffer_profile_id': self.buffer_profile_pur.id,
            'product_id': self.productA.id,
            'location_id': self.stock_location.id,
            'warehouse_id': self.warehouse.id,
            'product_min_qty': 0.0,
            'product_max_qty': 0.0,
            'qty_multiple': 0.0,
            'adu_calculation_method': method.id
        })
        self.orderpointModel.cron_ddmrp_adu()

        to_assert_value = 120 / 120
        self.assertEqual(orderpointA.adu, to_assert_value)

    def test_qualified_demand_1(self):
        """Moves within order spike horizon, outside the threshold but past
        or today's demand."""
        method = self.env.ref('ddmrp.adu_calculation_method_fixed')
        orderpointA = self.orderpointModel.create({
            'buffer_profile_id': self.buffer_profile_pur.id,
            'product_id': self.productA.id,
            'location_id': self.stock_location.id,
            'warehouse_id': self.warehouse.id,
            'product_min_qty': 0.0,
            'product_max_qty': 0.0,
            'qty_multiple': 0.0,
            'adu_calculation_method': method.id,
            'adu_fixed': 4,
            'adu': 4,
            'order_spike_horizon': 40
        })

        date_move = datetime.today()
        expected_result = orderpointA.order_spike_threshold * 2
        pickingOut1 = self.create_pickingoutA(
            date_move, expected_result)
        pickingOut1.action_confirm()
        self.orderpointModel.cron_ddmrp()
        self.assertEqual(orderpointA.qualified_demand, expected_result)

    def test_qualified_demand_2(self):
        """Moves within order spike horizon, below threshold. Should have no
        effect on the qualified demand."""
        method = self.env.ref('ddmrp.adu_calculation_method_fixed')
        orderpointA = self.orderpointModel.create({
            'buffer_profile_id': self.buffer_profile_pur.id,
            'product_id': self.productA.id,
            'location_id': self.stock_location.id,
            'warehouse_id': self.warehouse.id,
            'product_min_qty': 0.0,
            'product_max_qty': 0.0,
            'qty_multiple': 0.0,
            'adu_calculation_method': method.id,
            'adu_fixed': 4,
            'adu': 4,
            'order_spike_horizon': 40
        })

        date_move = datetime.today() + timedelta(days=10)
        self.create_pickingoutA(
            date_move, orderpointA.order_spike_threshold - 1)
        self.orderpointModel.cron_ddmrp()

        self.assertEqual(orderpointA.qualified_demand, 0)

    def test_qualified_demand_3(self):
        """Moves within order spike horizon, above threshold. Should have an
        effect on the qualified demand"""
        method = self.env.ref('ddmrp.adu_calculation_method_fixed')
        orderpointA = self.orderpointModel.create({
            'buffer_profile_id': self.buffer_profile_pur.id,
            'product_id': self.productA.id,
            'location_id': self.stock_location.id,
            'warehouse_id': self.warehouse.id,
            'product_min_qty': 0.0,
            'product_max_qty': 0.0,
            'qty_multiple': 0.0,
            'adu_calculation_method': method.id,
            'adu_fixed': 4,
            'adu': 4,
            'order_spike_horizon': 40
        })

        date_move = datetime.today() + timedelta(days=10)
        self.create_pickingoutA(date_move,
                                orderpointA.order_spike_threshold * 2)
        self.orderpointModel.cron_ddmrp()

        expected_result = orderpointA.order_spike_threshold * 2
        self.assertEqual(orderpointA.qualified_demand, expected_result)

    def test_qualified_demand_4(self):
        """ Moves outside of order spike horizon, above threshold. Should
        have no effect on the qualified demand"""
        method = self.env.ref('ddmrp.adu_calculation_method_fixed')
        orderpointA = self.orderpointModel.create({
            'buffer_profile_id': self.buffer_profile_pur.id,
            'product_id': self.productA.id,
            'location_id': self.stock_location.id,
            'warehouse_id': self.warehouse.id,
            'product_min_qty': 0.0,
            'product_max_qty': 0.0,
            'qty_multiple': 0.0,
            'adu_calculation_method': method.id,
            'adu_fixed': 4,
            'adu': 4,
            'order_spike_horizon': 40
        })

        date_move = datetime.today() + timedelta(days=100)
        self.create_pickingoutA(date_move,
                                orderpointA.order_spike_threshold * 2)
        self.orderpointModel.cron_ddmrp()

        expected_result = 0.0
        self.assertEqual(orderpointA.qualified_demand, expected_result)

    def test_qualified_demand_5(self):
        """Internal moves within the zone designated by the buffer
        should not be considered demand."""
        method = self.env.ref('ddmrp.adu_calculation_method_fixed')
        orderpointA = self.orderpointModel.create({
            'buffer_profile_id': self.buffer_profile_pur.id,
            'product_id': self.productA.id,
            'location_id': self.stock_location.id,
            'warehouse_id': self.warehouse.id,
            'product_min_qty': 0.0,
            'product_max_qty': 0.0,
            'qty_multiple': 0.0,
            'adu_calculation_method': method.id,
            'adu_fixed': 4,
            'adu': 4,
            'order_spike_horizon': 40
        })

        date_move = datetime.today()
        expected_result = 0
        pickingInternal = self.create_pickinginternalA(
            date_move, expected_result)
        pickingInternal.action_confirm()
        self.orderpointModel.cron_ddmrp()
        self.assertEqual(orderpointA.qualified_demand, expected_result)

    def _check_red_zone(self, orderpoint, red_base_qty=0.0, red_safety_qty=0.0,
                        red_zone_qty=0.0):

        # red base_qty = dlt * adu * lead time factor
        self.assertEqual(orderpoint.red_base_qty, red_base_qty)

        # red_safety_qty = red_base_qty * variability factor
        self.assertEqual(orderpoint.red_safety_qty, red_safety_qty)

        # red_zone_qty = red_base_qty + red_safety_qty
        self.assertEqual(orderpoint.red_zone_qty, red_zone_qty)

    def _check_yellow_zone(self, orderpoint, yellow_zone_qty=0.0,
                           top_of_yellow=0.0):

        # yellow_zone_qty = dlt * adu
        self.assertEqual(orderpoint.yellow_zone_qty, yellow_zone_qty)

        # top_of_yellow = yellow_zone_qty + red_zone_qty
        self.assertEqual(orderpoint.top_of_yellow, top_of_yellow)

    def _check_green_zone(self, orderpoint, green_zone_oc=0.0,
                          green_zone_lt_factor=0.0, green_zone_moq=0.0,
                          green_zone_qty=0.0, top_of_green=0.0):

        # green_zone_oc = order_cycle * adu
        self.assertEqual(orderpoint.green_zone_oc, green_zone_oc)

        # green_zone_lt_factor = dlt * adu * lead time factor
        self.assertEqual(orderpoint.green_zone_lt_factor, green_zone_lt_factor)

        # green_zone_moq = minimum_order_quantity
        self.assertEqual(orderpoint.green_zone_moq, green_zone_moq)

        # green_zone_qty = max(green_zone_oc, green_zone_lt_factor,
        # green_zone_moq)
        self.assertEqual(orderpoint.green_zone_qty, green_zone_qty)

        # top_of_green = green_zone_qty + yellow_zone_qty + red_zone_qty
        self.assertEqual(orderpoint.top_of_green, top_of_green)

    def test_buffer_zones_red(self):
        method = self.env.ref('ddmrp.adu_calculation_method_fixed')
        orderpointA = self.orderpointModel.create({
            'buffer_profile_id': self.buffer_profile_pur.id,
            'product_id': self.productA.id,
            'location_id': self.stock_location.id,
            'warehouse_id': self.warehouse.id,
            'product_min_qty': 0.0,
            'product_max_qty': 0.0,
            'qty_multiple': 0.0,
            'lead_days': 10,
            'adu_calculation_method': method.id,
            'adu_fixed': 4
        })
        self.orderpointModel.cron_ddmrp_adu()

        self._check_red_zone(orderpointA, red_base_qty=20, red_safety_qty=10,
                             red_zone_qty=30)

        orderpointA.lead_days = 20

        self._check_red_zone(orderpointA, red_base_qty=40, red_safety_qty=20,
                             red_zone_qty=60)

        orderpointA.buffer_profile_id.lead_time_id.factor = 1

        self._check_red_zone(orderpointA, red_base_qty=80, red_safety_qty=40,
                             red_zone_qty=120)

        orderpointA.buffer_profile_id.variability_id.factor = 1

        self._check_red_zone(orderpointA, red_base_qty=80, red_safety_qty=80,
                             red_zone_qty=160)

        orderpointA.adu_fixed = 2
        self.orderpointModel.cron_ddmrp_adu()

        self._check_red_zone(orderpointA, red_base_qty=40, red_safety_qty=40,
                             red_zone_qty=80)

    def test_buffer_zones_yellow(self):
        method = self.env.ref('ddmrp.adu_calculation_method_fixed')
        orderpointA = self.orderpointModel.create({
            'buffer_profile_id': self.buffer_profile_pur.id,
            'product_id': self.productA.id,
            'location_id': self.stock_location.id,
            'warehouse_id': self.warehouse.id,
            'product_min_qty': 0.0,
            'product_max_qty': 0.0,
            'qty_multiple': 0.0,
            'lead_days': 10,
            'adu_calculation_method': method.id,
            'adu_fixed': 4
        })
        self.orderpointModel.cron_ddmrp_adu()

        self._check_yellow_zone(orderpointA, yellow_zone_qty=40.0,
                                top_of_yellow=70.0)

        orderpointA.lead_days = 20

        self._check_yellow_zone(orderpointA, yellow_zone_qty=80.0,
                                top_of_yellow=140.0)

        orderpointA.adu_fixed = 2
        self.orderpointModel.cron_ddmrp_adu()

        self._check_yellow_zone(orderpointA, yellow_zone_qty=40.0,
                                top_of_yellow=70.0)

        orderpointA.buffer_profile_id.lead_time_id.factor = 1
        orderpointA.buffer_profile_id.variability_id.factor = 1

        self._check_yellow_zone(orderpointA, yellow_zone_qty=40.0,
                                top_of_yellow=120.0)

    def test_procure_recommended(self):
        method = self.env.ref('ddmrp.adu_calculation_method_fixed')
        orderpointA = self.orderpointModel.create({
            'buffer_profile_id': self.buffer_profile_pur.id,
            'product_id': self.productA.id,
            'location_id': self.stock_location.id,
            'warehouse_id': self.warehouse.id,
            'product_min_qty': 0.0,
            'product_max_qty': 0.0,
            'qty_multiple': 0.0,
            'lead_days': 10,
            'adu_calculation_method': method.id,
            'adu_fixed': 4
        })
        orderpointA._calc_adu()

        self.orderpointModel.cron_ddmrp()
        # Now we prepare the shipment of 150
        date_move = datetime.today()
        pickingOut = self.create_pickingoutA(date_move, 150)
        pickingOut.action_confirm()
        pickingOut.force_assign()
        pickingOut.move_lines.quantity_done = 150
        pickingOut.action_done()
        self.orderpointModel.cron_ddmrp()

        expected_value = 40.0
        self.assertEqual(orderpointA.procure_recommended_qty, expected_value)

        # Now we change the net flow position.
        # Net Flow position = 200 - 150 + 10 = 60
        self.quantModel.create(
            {'location_id': self.binA.id,
             'company_id': self.main_company.id,
             'product_id': self.productA.id,
             'quantity': 10.0})
        self.orderpointModel.cron_ddmrp()

        expected_value = 30.0
        self.assertEqual(orderpointA.procure_recommended_qty, expected_value)

        # Now we change the top of green.
        # red base = dlt * adu * lead time factor = 10 * 2 * 0.5 = 10
        # red safety = red_base * variability factor = 10 * 0.5 = 5
        # red zone = red_base + red_safety = 10 + 5 = 15
        # Top Of Red (TOR) = red zone = 15
        # yellow zone = dlt * adu = 10 * 2 = 20
        # Top Of Yellow (TOY) = TOR + yellow zone = 15 + 20 = 35
        # green_zone_oc = order_cycle * adu = 0 * 4 = 0
        # green_zone_lt_factor = dlt * adu * lead time factor =10
        # green_zone_moq = minimum_order_quantity = 0
        # green_zone_qty = max(green_zone_oc, green_zone_lt_factor,
        # green_zone_moq) = max(0, 10, 0) = 10
        # Top Of Green (TOG) = TOY + green_zone_qty = 35 + 10 = 45
        orderpointA.adu_fixed = 2
        self.orderpointModel.cron_ddmrp_adu()
        self.orderpointModel.cron_ddmrp()

        expected_value = 0
        self.assertEqual(orderpointA.procure_recommended_qty, expected_value)

        orderpointA.buffer_profile_id.lead_time_id.factor = 1
        # Now we change the top of green.
        # red base = dlt * adu * lead time factor = 10 * 2 * 1 = 20
        # red safety = red_base * variability factor = 20 * 0.5 = 10
        # red zone = red_base + red_safety = 20 + 10 = 30
        # Top Of Red (TOR) = red zone = 25
        # yellow zone = dlt * adu = 10 * 2 = 20
        # Top Of Yellow (TOY) = TOR + yellow zone = 30 + 20 = 50
        # green_zone_oc = order_cycle * adu = 0 * 4 = 0
        # green_zone_lt_factor = dlt * adu * lead time factor = 20
        # green_zone_moq = minimum_order_quantity = 0
        # green_zone_qty = max(green_zone_oc, green_zone_lt_factor,
        # green_zone_moq) = max(0, 20, 0) = 20
        # Top Of Green (TOG) = TOY + green_zone_qty = 50 + 20 = 70
        expected_value = 0
        self.assertEqual(orderpointA.procure_recommended_qty, expected_value)

        orderpointA.minimum_order_quantity = 40
        # Now we change the top of green.
        # red base = dlt * adu * lead time factor = 10 * 2 * 1 = 20
        # red safety = red_base * variability factor = 20 * 0.5 = 10
        # red zone = red_base + red_safety = 20 + 10 = 30
        # Top Of Red (TOR) = red zone = 25
        # yellow zone = dlt * adu = 10 * 2 = 20
        # Top Of Yellow (TOY) = TOR + yellow zone = 30 + 20 = 50
        # green_zone_oc = order_cycle * adu = 0 * 4 = 0
        # green_zone_lt_factor = dlt * adu * lead time factor = 20
        # green_zone_moq = minimum_order_quantity = 0
        # green_zone_qty = max(green_zone_oc, green_zone_lt_factor,
        # green_zone_moq) = max(0, 20, 40) = 40
        # Top Of Green (TOG) = TOY + green_zone_qty = 50 + 40 = 90
        expected_value = 0
        self.assertEqual(orderpointA.procure_recommended_qty, expected_value)

    def test_buffer_zones_all(self):
        method = self.env.ref('ddmrp.adu_calculation_method_fixed')
        orderpointA = self.orderpointModel.create({
            'buffer_profile_id': self.buffer_profile_pur.id,
            'product_id': self.productA.id,
            'location_id': self.stock_location.id,
            'warehouse_id': self.warehouse.id,
            'product_min_qty': 0.0,
            'product_max_qty': 0.0,
            'qty_multiple': 0.0,
            'lead_days': 10,
            'adu_calculation_method': method.id,
            'adu_fixed': 4
        })
        self.orderpointModel.cron_ddmrp_adu()
        # red base = dlt * adu * lead time factor = 10 * 4 * 0.5 = 20
        # red safety = red_base * variability factor = 20 * 0.5 = 10
        # red zone = red_base + red_safety = 20 + 10 = 30
        # Top Of Red (TOR) = red zone = 30
        self._check_red_zone(orderpointA, red_base_qty=20.0,
                             red_safety_qty=10.0,
                             red_zone_qty=30.0)

        # yellow zone = dlt * adu = 10 * 4 = 40
        # Top Of Yellow (TOY) = TOR + yellow zone = 30 + 40 = 70
        self._check_yellow_zone(orderpointA, yellow_zone_qty=40.0,
                                top_of_yellow=70.0)

        # green_zone_oc = order_cycle * adu = 0 * 4 = 0
        # green_zone_lt_factor = dlt * adu * lead time factor = 20
        # green_zone_moq = minimum_order_quantity = 0
        # green_zone_qty = max(green_zone_oc, green_zone_lt_factor,
        # green_zone_moq) = max(0, 20, 0) = 20
        # Top Of Green (TOG) = TOY + green_zone_qty = 70 + 20 = 90
        self._check_green_zone(orderpointA, green_zone_oc=0.0,
                               green_zone_lt_factor=20.0, green_zone_moq=0.0,
                               green_zone_qty=20.0, top_of_green=90.0)

        self.orderpointModel.cron_ddmrp()

        # Net Flow Position = on hand + incoming - qualified demand = 200 + 0
        #  - 0 = 200
        expected_value = 200.0
        self.assertEqual(orderpointA.net_flow_position, expected_value)

        # Net Flow Position Percent = (Net Flow Position / TOG)*100 = (
        # 200/90)*100 = 55.56 %
        expected_value = 222.22
        self.assertEqual(orderpointA.net_flow_position_percent, expected_value)

        # Planning priority level
        expected_value = '3_green'
        self.assertEqual(orderpointA.planning_priority_level, expected_value)

        # On hand/TOR = (200 / 30) * 100 = 666.67
        expected_value = 666.67
        self.assertEqual(orderpointA.on_hand_percent, expected_value)

        # Execution priority level
        expected_value = '3_green'
        self.assertEqual(orderpointA.execution_priority_level, expected_value)

        # Procure recommended quantity = TOG - Net Flow Position if > 0 = 90
        # - 200 => 0.0
        expected_value = 0.0
        self.assertEqual(orderpointA.procure_recommended_qty, expected_value)

        # Now we prepare the shipment of 150
        date_move = datetime.today()
        pickingOut = self.create_pickingoutA(date_move, 150)
        pickingOut.action_confirm()

        self.orderpointModel.cron_ddmrp()

        # Net Flow Position = on hand + incoming - qualified demand = 200 + 0
        #  - 150 = 50
        expected_value = 50.0
        self.assertEqual(orderpointA.net_flow_position, expected_value)

        # Net Flow Position Percent = (Net Flow Position / TOG)*100 = (
        # 50/90)*100 = 55.56 %
        expected_value = 55.56
        self.assertEqual(orderpointA.net_flow_position_percent, expected_value)

        # Planning priority level
        expected_value = '2_yellow'
        self.assertEqual(orderpointA.planning_priority_level, expected_value)

        # On hand/TOR = (200 / 30) * 100 = 666.67
        expected_value = 666.67
        self.assertEqual(orderpointA.on_hand_percent, expected_value)

        # Execution priority level
        expected_value = '3_green'
        self.assertEqual(orderpointA.execution_priority_level, expected_value)

        # Now we confirm the shipment of the 150
        pickingOut.action_assign()
        pickingOut.force_assign()
        pickingOut.move_lines.quantity_done = 150
        pickingOut.action_done()
        self.orderpointModel.cron_ddmrp()

        # On hand/TOR = (50 / 30) * 100 = 166.67
        expected_value = 166.67
        self.assertEqual(orderpointA.on_hand_percent, expected_value)

        # Execution priority level. Considering that the quantity available
        # unrestricted is 50, and top of red is 30, we are in the green on
        # hand zone.
        expected_value = '3_green'
        self.assertEqual(orderpointA.execution_priority_level, expected_value)

        # Procure recommended quantity = TOG - Net Flow Position if > 0 = 90
        # - 50 => 40.0
        expected_value = 40.0
        self.assertEqual(orderpointA.procure_recommended_qty, expected_value)

        # Now we ship them
        pickingOut.action_done()
        self.orderpointModel.cron_ddmrp()

        # Net Flow Position = on hand + incoming - qualified demand = 200 + 0
        #  - 150 = 50
        expected_value = 50.0
        self.assertEqual(orderpointA.net_flow_position, expected_value)

        # Net Flow Position Percent = (Net Flow Position / TOG)*100 = (
        # 50/90)*100 = 55.56 %
        expected_value = 55.56
        self.assertEqual(orderpointA.net_flow_position_percent, expected_value)

        # Planning priority level
        expected_value = '2_yellow'
        self.assertEqual(orderpointA.planning_priority_level, expected_value)

        # On hand/TOR = (50 / 30) * 100 = 166.67
        expected_value = 166.67
        self.assertEqual(orderpointA.on_hand_percent, expected_value)

        # Execution priority level
        expected_value = '3_green'
        self.assertEqual(orderpointA.execution_priority_level, expected_value)

        # Procure recommended quantity = TOG - Net Flow Position if > 0 = 90
        # - 50 => 40.0
        expected_value = 40.0
        self.assertEqual(orderpointA.procure_recommended_qty, expected_value)

        # Now we create a procurement order, based on the procurement
        # recommendation
        self.create_orderpoint_procurement(orderpointA)
        # should have generated a manufacturing order
        self.assertEqual(len(orderpointA.mrp_production_ids), 1)
        self.assertEqual(orderpointA.mrp_production_ids.product_qty, 40.0)

        # We expect that the procurement recommendation is now 0
        expected_value = 0.0
        self.assertEqual(orderpointA.procure_recommended_qty, expected_value)

    def test_bom_orderpoint(self):
        # Check if is_buffered and orderpoint_id are not set
        self.assertEqual(self.bomA.is_buffered, False)
        self.assertEqual(len(self.bomA.orderpoint_id), 0)
        product = self.productA
        orderpointA = self.orderpointModel.create({
            'buffer_profile_id': self.buffer_profile_pur.id,
            'product_id': product.id,
            'warehouse_id': self.warehouse.id,
            'product_min_qty': 0.0,
            'product_max_qty': 0.0,
        })
        # Create a new bom to trigger the compute functions
        bomB = self.bomModel.create({
            'product_id': product.id,
            'product_tmpl_id': product.product_tmpl_id.id,
        })
        # Check if is_buffered and orderpoint_id are set
        self.assertEqual(bomB.is_buffered, True)
        self.assertEqual(bomB.orderpoint_id, orderpointA)
        # Create another orderpoint with a location, then change the bom
        # location
        orderpointB = self.orderpointModel.create({
            'buffer_profile_id': self.buffer_profile_pur.id,
            'product_id': product.id,
            'warehouse_id': self.warehouse.id,
            'location_id': self.supplier_location.id,
            'product_min_qty': 0.0,
            'product_max_qty': 0.0,
        })
        bomB.location_id = self.supplier_location.id
        self.assertEqual(bomB.is_buffered, True)
        self.assertEqual(bomB.orderpoint_id, orderpointB)
        bomC = self.env['mrp.bom'].create({
            'product_tmpl_id': product.product_tmpl_id.id
        })
        self.assertEqual(bomC.is_buffered, True)
        self.assertEqual(bomC.orderpoint_id, orderpointA)


class TestBomDLT(common.TransactionCase):
    def setUp(self):
        super(TestBomDLT, self).setUp()
        self.orderpointModel = self.env['stock.warehouse.orderpoint']
        self.buffer_profile_mmm = self.env.ref(
            'ddmrp.stock_buffer_profile_replenish_manufactured_medium_medium')
        self.warehouse = self.env.ref('stock.warehouse0')
        self.stock_location = self.env.ref('stock.stock_location_stock')

    def test_01_bom_dlt_computation(self):
        """Tests that DLT computation is correct adding/removing buffers."""
        bom_fp01 = self.env.ref('ddmrp.mrp_bom_fp01')
        self.assertEqual(bom_fp01.dlt, 22)
        # Remove RM-01 buffer:
        orderpoint_rm01 = self.env.ref('ddmrp.stock_warehouse_orderpoint_rm01')
        orderpoint_rm01.unlink()
        self.assertEqual(bom_fp01.dlt, 33.0)

    def test_02_bom_dlt_computation(self):
        # Add buffer on AS-01
        product_as01 = self.env.ref('ddmrp.product_product_as01')
        self.orderpointModel.create({
            'buffer_profile_id': self.buffer_profile_mmm.id,
            'product_id': product_as01.id,
            'warehouse_id': self.warehouse.id,
            'location_id': self.stock_location.id,
            'product_min_qty': 0.0,
            'product_max_qty': 0.0,
        })
        bom_fp01 = self.env.ref('ddmrp.mrp_bom_fp01')
        self.assertEqual(bom_fp01.dlt, 2.0)
