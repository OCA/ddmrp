# Copyright 2016-20 ForgeFlow S.L. (http://www.forgeflow.com)
# Copyright 2016 Aleph Objects, Inc. (https://www.alephobjects.com/)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from datetime import datetime, timedelta

from odoo.exceptions import ValidationError

from odoo.addons.ddmrp.tests.common import TestDdmrpCommon


class TestDdmrp(TestDdmrpCommon):

    # TEST GROUP 1: ADU and Spikes

    def test_01_adu_calculation_fixed(self):
        """Test fixed ADU assigned correctly with fixed method."""
        self.bufferModel.cron_ddmrp_adu()
        to_assert_value = 4
        self.assertEqual(self.buffer_a.adu, to_assert_value)

    def test_02_adu_calculation_past_120_days(self):
        """Test ADU calculation method that uses actual past stock moves,
        excepting inventory loss moves.
        """
        method = self.env.ref("ddmrp.adu_calculation_method_past_120")
        self.buffer_a.adu_calculation_method = method.id
        self.bufferModel.cron_ddmrp_adu()
        self.assertEqual(self.buffer_a.adu, 0)
        # Create past moves and process them.
        days = 30
        date_move = self.calendar.plan_days(-1 * days - 1, datetime.today())
        move_inv_loss = self.create_inventorylossA(date_move, 10)
        self._do_move(move_inv_loss, date_move)
        pick_out_1 = self.create_pickingoutA(date_move, 60)
        self._do_picking(pick_out_1, date_move)
        days = 60
        date_move = self.calendar.plan_days(-1 * days - 1, datetime.today())
        pick_out_2 = self.create_pickingoutA(date_move, 60)
        self._do_picking(pick_out_2, date_move)
        # Compute ADU again and check result.
        self.bufferModel.cron_ddmrp_adu()
        to_assert_value = (60 + 60) / 120  # Doesn't include inventory loss qty
        self.assertEqual(self.buffer_a.adu, to_assert_value)

    def test_03_adu_calculation_window_past(self):
        """Test that the window considered to calculate the ADU is correct."""
        self.warehouse.calendar_id = False
        method = self.aducalcmethodModel.create(
            {
                "name": "Past actual demand (6 days)",
                "method": "past",
                "source_past": "actual",
                "horizon_past": 6,
                "company_id": self.main_company.id,
            }
        )
        self.buffer_a.adu_calculation_method = method.id
        # Today should be excluded
        date_move_1 = datetime.today()
        picking_1 = self.create_pickingoutA(date_move_1, 20)
        self._do_picking(picking_1, date_move_1)
        # The next moves should be considered
        date_move_2 = datetime.today() - timedelta(days=1)
        picking_2 = self.create_pickingoutA(date_move_2, 20)
        self._do_picking(picking_2, date_move_2)
        date_move_3 = datetime.today() - timedelta(days=4)
        picking_3 = self.create_pickingoutA(date_move_3, 20)
        self._do_picking(picking_3, date_move_3)
        date_move_4 = datetime.today() - timedelta(days=6)
        picking_4 = self.create_pickingoutA(date_move_4, 10)
        self._do_picking(picking_4, date_move_4)
        # This move should be ignored
        date_move_5 = datetime.today() - timedelta(days=7)
        picking_5 = self.create_pickingoutA(date_move_5, 12)
        self._do_picking(picking_5, date_move_5)

        # Check ADU:
        self.buffer_a._calc_adu()
        to_assert_value = (20 + 20 + 10) / 6
        self.assertAlmostEqual(self.buffer_a.adu, to_assert_value, places=2)

    def test_04_adu_calculation_window_past_calendar(self):
        """Test that the window considered to calculate the ADU is correct.
        (With working days set)."""
        self.warehouse.calendar_id = self.calendar
        method = self.aducalcmethodModel.create(
            {
                "name": "Past actual demand (6 days)",
                "method": "past",
                "source_past": "actual",
                "horizon_past": 6,
                "company_id": self.main_company.id,
            }
        )
        self.buffer_a.adu_calculation_method = method.id
        # Today should be excluded
        date_move_1 = datetime.today()
        picking_1 = self.create_pickingoutA(date_move_1, 20)
        self._do_picking(picking_1, date_move_1)
        # The next moves should be considered
        days = 2
        date_move_2 = self.calendar.plan_days(-1 * days - 1, datetime.today())
        picking_2 = self.create_pickingoutA(date_move_2, 20)
        self._do_picking(picking_2, date_move_2)
        days = 4
        date_move_3 = self.calendar.plan_days(-1 * days - 1, datetime.today())
        picking_3 = self.create_pickingoutA(date_move_3, 20)
        self._do_picking(picking_3, date_move_3)
        days = 6
        date_move_4 = self.calendar.plan_days(-1 * days - 1, datetime.today())
        picking_4 = self.create_pickingoutA(date_move_4, 10)
        self._do_picking(picking_4, date_move_4)
        # This move should be ignored
        days = 7
        date_move_5 = self.calendar.plan_days(-1 * days - 1, datetime.today())
        picking_5 = self.create_pickingoutA(date_move_5, 12)
        self._do_picking(picking_5, date_move_5)

        # Check ADU:
        self.buffer_a._calc_adu()
        to_assert_value = (20 + 20 + 10) / 6
        self.assertAlmostEqual(self.buffer_a.adu, to_assert_value, places=2)

    def test_05_adu_calculation_internal_past_120_days(self):
        """Test that internal moves will not affect ADU calculation."""
        method = self.env.ref("ddmrp.adu_calculation_method_past_120")
        self.buffer_a.adu_calculation_method = method.id
        self.bufferModel.cron_ddmrp_adu()
        self.assertEqual(self.buffer_a.adu, 0)

        pickingInternals = self.pickingModel
        days = 30
        date_move = self.calendar.plan_days(-1 * days - 1, datetime.today())
        pickingInternals += self.create_pickinginternalA(date_move, 60)
        days = 60
        date_move = self.calendar.plan_days(-1 * days - 1, datetime.today())
        pickingInternals += self.create_pickinginternalA(date_move, 60)
        for picking in pickingInternals:
            picking.action_assign()
            picking._action_done()

        self.bufferModel.cron_ddmrp_adu()

        to_assert_value = 0
        self.assertEqual(self.buffer_a.adu, to_assert_value)

    def test_06_adu_calculation_future_120_days_actual(self):
        """Test ADU calculation method that uses actual future stock moves,
        excepting inventory loss moves.
        """
        method = self.aducalcmethodModel.create(
            {
                "name": "Future actual demand (120 days)",
                "method": "future",
                "source_future": "actual",
                "horizon_future": 120,
                "company_id": self.main_company.id,
            }
        )
        self.buffer_a.adu_calculation_method = method.id

        pickingOuts = self.pickingModel
        days = 30
        date_move = self.calendar.plan_days(+1 * days + 1, datetime.today())
        move_inv_loss = self.create_inventorylossA(date_move, 10)
        self._do_move(move_inv_loss, date_move)
        pickingOuts += self.create_pickingoutA(date_move, 60)
        days = 60
        date_move = self.calendar.plan_days(+1 * days + 1, datetime.today())
        pickingOuts += self.create_pickingoutA(date_move, 60)

        self.bufferModel.cron_ddmrp_adu()
        to_assert_value = (60 + 60) / 120  # Doesn't include inventory loss qty
        self.assertEqual(self.buffer_a.adu, to_assert_value)

        # Create a move more than 120 days in the future
        days = 150
        date_move = self.calendar.plan_days(+1 * days + 1, datetime.today())
        pickingOuts += self.create_pickingoutA(date_move, 1)

        # The extra move should not affect to the average ADU
        self.assertEqual(self.buffer_a.adu, to_assert_value)

    def test_07_adu_calculation_future_120_days_estimated(self):
        method = self.env.ref("ddmrp.adu_calculation_method_future_120")
        self.estimateModel.create(
            {
                "manual_date_from": self.estimate_date_from,
                "manual_date_to": self.estimate_date_to,
                "product_id": self.productA.id,
                "product_uom_qty": 120,
                "product_uom": self.productA.uom_id.id,
                "location_id": self.stock_location.id,
            }
        )
        self.buffer_a.adu_calculation_method = method.id
        self.bufferModel.cron_ddmrp_adu()
        to_assert_value = 120 / 120
        self.assertEqual(self.buffer_a.adu, to_assert_value)

    def test_08_adu_calculation_blended(self):
        """Test blended ADU calculation method."""
        method = self.aducalcmethodModel.create(
            {
                "name": "Blended (120 d. actual past, 120 d. estimates future)",
                "method": "blended",
                "source_past": "actual",
                "horizon_past": 120,
                "factor_past": 0.5,
                "source_future": "estimates",
                "horizon_future": 120,
                "factor_future": 0.5,
                "company_id": self.main_company.id,
            }
        )
        self.buffer_a.adu_calculation_method = method.id

        # Past. Generate past moves: 360 units / 120 days = 3 unit/day
        days = 30
        date_move = self.calendar.plan_days(-1 * days - 1, datetime.today())
        pick_out_1 = self.create_pickingoutA(date_move, 180)
        self._do_picking(pick_out_1, date_move)
        days = 60
        date_move = self.calendar.plan_days(-1 * days - 1, datetime.today())
        pick_out_2 = self.create_pickingoutA(date_move, 180)
        self._do_picking(pick_out_2, date_move)

        # Future. create estimate: 120 units / 120 days = 1 unit/day
        self.estimateModel.create(
            {
                "manual_date_from": self.estimate_date_from,
                "manual_date_to": self.estimate_date_to,
                "product_id": self.productA.id,
                "product_uom_qty": 120,
                "product_uom": self.productA.uom_id.id,
                "location_id": self.stock_location.id,
            }
        )
        self.bufferModel.cron_ddmrp_adu()
        to_assert_value = 3 * 0.5 + 1 * 0.5
        self.assertEqual(self.buffer_a.adu, to_assert_value)

    def test_09_adu_calculation_method_checks(self):
        with self.assertRaises(ValidationError):
            # missing horizon_past
            self.aducalcmethodModel.create(
                {
                    "name": "error horizon_past",
                    "method": "past",
                    "source_past": "actual",
                    "factor_past": 0.5,
                    "company_id": self.main_company.id,
                }
            )
        with self.assertRaises(ValidationError):
            # missing horizon_future
            self.aducalcmethodModel.create(
                {
                    "name": "error horizon_future",
                    "method": "future",
                    "source_future": "estimates",
                    "factor_future": 0.5,
                    "company_id": self.main_company.id,
                }
            )
        with self.assertRaises(ValidationError):
            # missing source_past
            self.aducalcmethodModel.create(
                {
                    "name": "error source_past",
                    "method": "past",
                    "horizon_past": 120,
                    "factor_past": 0.5,
                    "company_id": self.main_company.id,
                }
            )
        with self.assertRaises(ValidationError):
            # missing source_future
            self.aducalcmethodModel.create(
                {
                    "name": "error source_future",
                    "method": "future",
                    "horizon_future": 120,
                    "factor_future": 0.5,
                    "company_id": self.main_company.id,
                }
            )
        with self.assertRaises(ValidationError):
            # wrong factors for blended
            self.aducalcmethodModel.create(
                {
                    "name": "error factors",
                    "method": "blended",
                    "source_past": "actual",
                    "horizon_past": 30,
                    "factor_past": 0.2,
                    "source_future": "estimates",
                    "horizon_future": 30,
                    "factor_future": 0.6,
                    "company_id": self.main_company.id,
                }
            )

    def test_10_qualified_demand_1(self):
        """Moves within order spike horizon, outside the threshold but past
        or today's demand."""
        date_move = datetime.today()
        expected_result = self.buffer_a.order_spike_threshold * 2
        self.create_pickingoutA(date_move, expected_result)
        self.bufferModel.cron_ddmrp()
        self.assertEqual(self.buffer_a.qualified_demand, expected_result)

    def test_11_qualified_demand_2(self):
        """Moves within order spike horizon, below threshold. Should have no
        effect on the qualified demand."""
        date_move = datetime.today() + timedelta(days=10)
        self.create_pickingoutA(date_move, self.buffer_a.order_spike_threshold - 1)
        self.bufferModel.cron_ddmrp()
        expected_result = 0.0
        self.assertEqual(self.buffer_a.qualified_demand, expected_result)

    def test_12_qualified_demand_3(self):
        """Moves within order spike horizon, above threshold. Should have an
        effect on the qualified demand"""
        date_move = datetime.today() + timedelta(days=10)
        self.create_pickingoutA(date_move, self.buffer_a.order_spike_threshold * 2)
        self.bufferModel.cron_ddmrp()
        expected_result = self.buffer_a.order_spike_threshold * 2
        self.assertEqual(self.buffer_a.qualified_demand, expected_result)

    def test_13_qualified_demand_4(self):
        """Moves outside of order spike horizon, above threshold. Should
        have no effect on the qualified demand"""
        date_move = datetime.today() + timedelta(days=100)
        self.create_pickingoutA(date_move, self.buffer_a.order_spike_threshold * 2)
        self.bufferModel.cron_ddmrp()
        expected_result = 0.0
        self.assertEqual(self.buffer_a.qualified_demand, expected_result)

    def test_14_qualified_demand_5(self):
        """Internal moves within the zone designated by the buffer
        should not be considered demand."""
        date_move = datetime.today()
        expected_result = 0
        self.create_pickinginternalA(date_move, expected_result)
        self.bufferModel.cron_ddmrp()
        self.assertEqual(self.buffer_a.qualified_demand, expected_result)

    def test_15_incoming_quantity_1(self):
        date_move = datetime.today() + timedelta(days=5)
        self.create_pickinginA(date_move, 20)
        self.bufferModel.cron_ddmrp()
        self.assertEqual(self.buffer_a.incoming_dlt_qty, 20.0)

    def test_16_incoming_quantity_2(self):
        """Moves outside the DLT horizon are ignored as supply"""
        date_move = datetime.today() + timedelta(days=100)
        self.create_pickinginA(date_move, 20)
        self.bufferModel.cron_ddmrp()
        self.assertEqual(self.buffer_a.incoming_dlt_qty, 0.0)
        self.assertEqual(self.buffer_a.incoming_outside_dlt_qty, 20.0)

    def test_17_on_hand_qty_1(self):
        """Outgoing moves should be ignored once reserved as well as the
        reserved qty."""
        date_move = datetime.today()
        outgoing_qty = 50
        picking = self.create_pickingoutA(date_move, outgoing_qty)
        self.buffer_a.cron_actions()
        self.assertEqual(self.buffer_a.qualified_demand, outgoing_qty)
        expected_on_hand = 200
        self.assertEqual(
            self.buffer_a.product_location_qty_available_not_res, expected_on_hand
        )
        # Once reserved, the outgoing qty is not considered for qualified
        # demand and it is excluded from on hand position:
        picking.action_assign()
        self.buffer_a.invalidate_cache()
        self.buffer_a.cron_actions()
        self.assertEqual(self.buffer_a.qualified_demand, 0)
        expected_on_hand = 200
        self.assertEqual(
            self.buffer_a.product_location_qty_available_not_res,
            expected_on_hand - outgoing_qty,
        )

    def test_18_on_hand_qty_2(self):
        """Internal moves should not affect in any way the on hand position of
        a buffer."""
        date_move = datetime.today()
        internal_qty = 50
        picking = self.create_pickinginternalA(date_move, internal_qty)
        self.buffer_a.cron_actions()
        self.assertEqual(self.buffer_a.qualified_demand, 0)
        expected_on_hand = 200
        self.assertEqual(
            self.buffer_a.product_location_qty_available_not_res, expected_on_hand
        )
        # Once reserved, the internal qty is still considered in the on hand position:
        picking.action_assign()
        self.buffer_a.invalidate_cache()
        self.buffer_a.cron_actions()
        self.assertEqual(picking.move_lines.reserved_availability, internal_qty)
        self.assertEqual(self.buffer_a.qualified_demand, 0)
        expected_on_hand = 200
        self.assertEqual(
            self.buffer_a.product_location_qty_available_not_res, expected_on_hand
        )

    # TEST GROUP 2: Buffer zones and procurement

    def _check_red_zone(
        self, orderpoint, red_base_qty=0.0, red_safety_qty=0.0, red_zone_qty=0.0
    ):

        # red base_qty = dlt * adu * lead time factor
        self.assertEqual(orderpoint.red_base_qty, red_base_qty)

        # red_safety_qty = red_base_qty * variability factor
        self.assertEqual(orderpoint.red_safety_qty, red_safety_qty)

        # red_zone_qty = red_base_qty + red_safety_qty
        self.assertEqual(orderpoint.red_zone_qty, red_zone_qty)

    def _check_yellow_zone(self, orderpoint, yellow_zone_qty=0.0, top_of_yellow=0.0):

        # yellow_zone_qty = dlt * adu
        self.assertEqual(orderpoint.yellow_zone_qty, yellow_zone_qty)

        # top_of_yellow = yellow_zone_qty + red_zone_qty
        self.assertEqual(orderpoint.top_of_yellow, top_of_yellow)

    def _check_green_zone(
        self,
        orderpoint,
        green_zone_oc=0.0,
        green_zone_lt_factor=0.0,
        green_zone_moq=0.0,
        green_zone_qty=0.0,
        top_of_green=0.0,
    ):

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

    def test_20_buffer_zones_red(self):
        self._check_red_zone(
            self.buffer_a, red_base_qty=20, red_safety_qty=10, red_zone_qty=30
        )

        self.buffer_a.lead_days = 20
        self._check_red_zone(
            self.buffer_a, red_base_qty=40, red_safety_qty=20, red_zone_qty=60
        )

        self.buffer_a.buffer_profile_id.lead_time_id.factor = 1
        self._check_red_zone(
            self.buffer_a, red_base_qty=80, red_safety_qty=40, red_zone_qty=120
        )

        self.buffer_a.buffer_profile_id.variability_id.factor = 1
        self._check_red_zone(
            self.buffer_a, red_base_qty=80, red_safety_qty=80, red_zone_qty=160
        )

        self.buffer_a.adu_fixed = 2
        self.bufferModel.cron_ddmrp_adu()
        self._check_red_zone(
            self.buffer_a, red_base_qty=40, red_safety_qty=40, red_zone_qty=80
        )

    def test_21_buffer_zones_yellow(self):
        self._check_yellow_zone(self.buffer_a, yellow_zone_qty=40.0, top_of_yellow=70.0)

        self.buffer_a.lead_days = 20
        self._check_yellow_zone(
            self.buffer_a, yellow_zone_qty=80.0, top_of_yellow=140.0
        )

        self.buffer_a.adu_fixed = 2
        self.bufferModel.cron_ddmrp_adu()
        self._check_yellow_zone(self.buffer_a, yellow_zone_qty=40.0, top_of_yellow=70.0)

        self.buffer_a.buffer_profile_id.lead_time_id.factor = 1
        self.buffer_a.buffer_profile_id.variability_id.factor = 1
        self._check_yellow_zone(
            self.buffer_a, yellow_zone_qty=40.0, top_of_yellow=120.0
        )

    def test_22_procure_recommended(self):
        self.buffer_a._calc_adu()
        self.bufferModel.cron_ddmrp()
        # Now we prepare the shipment of 150
        date_move = datetime.today()
        pickingOut = self.create_pickingoutA(date_move, 150)
        pickingOut.move_lines.quantity_done = 150
        pickingOut._action_done()
        self.bufferModel.cron_ddmrp()

        expected_value = 40.0
        self.assertEqual(self.buffer_a.procure_recommended_qty, expected_value)

        # Now we change the net flow position.
        # Net Flow position = 200 - 150 + 10 = 60
        self.quantModel.create(
            {
                "location_id": self.binA.id,
                "company_id": self.main_company.id,
                "product_id": self.productA.id,
                "quantity": 10.0,
            }
        )
        self.bufferModel.cron_ddmrp()

        expected_value = 30.0
        self.assertEqual(self.buffer_a.procure_recommended_qty, expected_value)

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
        self.buffer_a.adu_fixed = 2
        self.bufferModel.cron_ddmrp_adu()
        self.bufferModel.cron_ddmrp()

        expected_value = 0
        self.assertEqual(self.buffer_a.procure_recommended_qty, expected_value)

        self.buffer_a.buffer_profile_id.lead_time_id.factor = 1
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
        self.assertEqual(self.buffer_a.procure_recommended_qty, expected_value)

        self.buffer_a.minimum_order_quantity = 40
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
        self.assertEqual(self.buffer_a.procure_recommended_qty, expected_value)

    def test_23_buffer_zones_all(self):
        self.bufferModel.cron_ddmrp_adu()
        # red base = dlt * adu * lead time factor = 10 * 4 * 0.5 = 20
        # red safety = red_base * variability factor = 20 * 0.5 = 10
        # red zone = red_base + red_safety = 20 + 10 = 30
        # Top Of Red (TOR) = red zone = 30
        self._check_red_zone(
            self.buffer_a, red_base_qty=20.0, red_safety_qty=10.0, red_zone_qty=30.0
        )

        # yellow zone = dlt * adu = 10 * 4 = 40
        # Top Of Yellow (TOY) = TOR + yellow zone = 30 + 40 = 70
        self._check_yellow_zone(self.buffer_a, yellow_zone_qty=40.0, top_of_yellow=70.0)

        # green_zone_oc = order_cycle * adu = 0 * 4 = 0
        # green_zone_lt_factor = dlt * adu * lead time factor = 20
        # green_zone_moq = minimum_order_quantity = 0
        # green_zone_qty = max(green_zone_oc, green_zone_lt_factor,
        # green_zone_moq) = max(0, 20, 0) = 20
        # Top Of Green (TOG) = TOY + green_zone_qty = 70 + 20 = 90
        self._check_green_zone(
            self.buffer_a,
            green_zone_oc=0.0,
            green_zone_lt_factor=20.0,
            green_zone_moq=0.0,
            green_zone_qty=20.0,
            top_of_green=90.0,
        )

        self.bufferModel.cron_ddmrp()

        # Net Flow Position = on hand + incoming - qualified demand = 200 + 0
        #  - 0 = 200
        expected_value = 200.0
        self.assertEqual(self.buffer_a.net_flow_position, expected_value)

        # Net Flow Position Percent = (Net Flow Position / TOG)*100 = (
        # 200/90)*100 = 55.56 %
        expected_value = 222.22
        self.assertEqual(self.buffer_a.net_flow_position_percent, expected_value)

        # Planning priority level
        expected_value = "3_green"
        self.assertEqual(self.buffer_a.planning_priority_level, expected_value)

        # On hand/TOR = (200 / 30) * 100 = 666.67
        expected_value = 666.67
        self.assertEqual(self.buffer_a.on_hand_percent, expected_value)

        # Execution priority level
        expected_value = "3_green"
        self.assertEqual(self.buffer_a.execution_priority_level, expected_value)

        # Procure recommended quantity = TOG - Net Flow Position if > 0 = 90
        # - 200 => 0.0
        expected_value = 0.0
        self.assertEqual(self.buffer_a.procure_recommended_qty, expected_value)

        # Now we prepare the shipment of 150
        date_move = datetime.today()
        pickingOut = self.create_pickingoutA(date_move, 150)

        self.bufferModel.cron_ddmrp()

        # Net Flow Position = on hand + incoming - qualified demand = 200 + 0
        #  - 150 = 50
        expected_value = 50.0
        self.assertEqual(self.buffer_a.net_flow_position, expected_value)

        # Net Flow Position Percent = (Net Flow Position / TOG)*100 = (
        # 50/90)*100 = 55.56 %
        expected_value = 55.56
        self.assertEqual(self.buffer_a.net_flow_position_percent, expected_value)

        # Planning priority level
        expected_value = "2_yellow"
        self.assertEqual(self.buffer_a.planning_priority_level, expected_value)

        # On hand/TOR = (200 / 30) * 100 = 666.67
        expected_value = 666.67
        self.assertEqual(self.buffer_a.on_hand_percent, expected_value)

        # Execution priority level
        expected_value = "3_green"
        self.assertEqual(self.buffer_a.execution_priority_level, expected_value)

        # Now we confirm the shipment of the 150
        pickingOut.action_assign()
        pickingOut.move_lines.quantity_done = 150
        pickingOut._action_done()
        self.bufferModel.cron_ddmrp()

        # On hand/TOR = (50 / 30) * 100 = 166.67
        expected_value = 166.67
        self.assertEqual(self.buffer_a.on_hand_percent, expected_value)

        # Execution priority level. Considering that the quantity available
        # unrestricted is 50, and top of red is 30, we are in the green on
        # hand zone.
        expected_value = "3_green"
        self.assertEqual(self.buffer_a.execution_priority_level, expected_value)

        # Procure recommended quantity = TOG - Net Flow Position if > 0 = 90
        # - 50 => 40.0
        expected_value = 40.0
        self.assertEqual(self.buffer_a.procure_recommended_qty, expected_value)

        # Now we ship them
        pickingOut._action_done()
        self.bufferModel.cron_ddmrp()

        # Net Flow Position = on hand + incoming - qualified demand = 200 + 0
        #  - 150 = 50
        expected_value = 50.0
        self.assertEqual(self.buffer_a.net_flow_position, expected_value)

        # Net Flow Position Percent = (Net Flow Position / TOG)*100 = (
        # 50/90)*100 = 55.56 %
        expected_value = 55.56
        self.assertEqual(self.buffer_a.net_flow_position_percent, expected_value)

        # Planning priority level
        expected_value = "2_yellow"
        self.assertEqual(self.buffer_a.planning_priority_level, expected_value)

        # On hand/TOR = (50 / 30) * 100 = 166.67
        expected_value = 166.67
        self.assertEqual(self.buffer_a.on_hand_percent, expected_value)

        # Execution priority level
        expected_value = "3_green"
        self.assertEqual(self.buffer_a.execution_priority_level, expected_value)

        # Procure recommended quantity = TOG - Net Flow Position if > 0 = 90
        # - 50 => 40.0
        expected_value = 40.0
        self.assertEqual(self.buffer_a.procure_recommended_qty, expected_value)

        # Now we create a procurement order, based on the procurement
        # recommendation
        self.create_orderpoint_procurement(self.buffer_a)
        # should have generated a manufacturing order
        self.assertEqual(len(self.buffer_a.mrp_production_ids), 1)
        self.assertEqual(self.buffer_a.mrp_production_ids.product_qty, 40.0)

        # We expect that the procurement recommendation is now 0
        expected_value = 0.0
        self.assertEqual(self.buffer_a.procure_recommended_qty, expected_value)

    def test_24_purchase_link(self):
        pol = self.pol_model.search([("product_id", "=", self.product_purchased.id)])
        self.assertFalse(pol)
        self.assertGreater(self.buffer_purchase.procure_recommended_qty, 0)
        self.create_orderpoint_procurement(self.buffer_purchase)
        pol = self.pol_model.search([("product_id", "=", self.product_purchased.id)])
        self.assertEqual(len(pol), 1)
        self.assertIn(pol.buffer_ids, self.buffer_purchase)
        self.assertEqual(self.buffer_purchase.procure_recommended_qty, 0)

    def test_25_auto_procure(self):
        pol = self.pol_model.search([("product_id", "=", self.product_purchased.id)])
        self.assertFalse(pol)
        self.assertGreater(self.buffer_purchase.procure_recommended_qty, 0)
        self.buffer_purchase.auto_procure = True
        self.buffer_purchase.auto_procure_option = "stockout"
        self.buffer_purchase.cron_actions()
        pol = self.pol_model.search([("product_id", "=", self.product_purchased.id)])
        self.assertFalse(pol)  # Buffer is not in stockout.
        # Change to standard, it should procure now.
        self.buffer_purchase.auto_procure_option = "standard"
        self.buffer_purchase.cron_actions()
        pol = self.pol_model.search([("product_id", "=", self.product_purchased.id)])
        self.assertEqual(len(pol), 1)
        self.assertEqual(self.buffer_purchase.procure_recommended_qty, 0)

    def test_26_auto_procure_stockout_and_auto_nfp(self):
        self.main_company.ddmrp_auto_update_nfp = True
        self.buffer_purchase.auto_procure = True
        self.buffer_purchase.auto_procure_option = "stockout"
        pol = self.pol_model.search([("product_id", "=", self.product_purchased.id)])
        self.assertFalse(pol)
        initial_nfp = self.buffer_purchase.net_flow_position
        self.assertEqual(initial_nfp, 0)
        # Provoke an stockout:
        date_move = datetime.today()
        p_out_1 = self.create_picking_out(self.product_purchased, date_move, 10)
        self._do_picking(p_out_1, date_move)
        # A RFQ should have been created.
        self.assertEqual(self.buffer_purchase.net_flow_position, -10)
        pol = self.pol_model.search([("product_id", "=", self.product_purchased.id)])
        self.assertEqual(len(pol), 1)
        self.assertEqual(self.buffer_purchase.procure_recommended_qty, 0)

    def test_27_qty_multiple_tolerance(self):
        buffer = self.bufferModel.create(
            {
                "buffer_profile_id": self.buffer_profile_override.id,
                "product_id": self.product_purchased.id,
                "location_id": self.stock_location.id,
                "warehouse_id": self.warehouse.id,
                "qty_multiple": 250.0,
                "adu_calculation_method": self.adu_fixed.id,
                "adu_fixed": 5.0,
                "green_override": 250.0,
                "yellow_override": 10.0,
                "red_override": 10.0,
            }
        )
        date_move = datetime.today()
        self.create_picking_out(self.product_purchased, date_move, 2)
        buffer.cron_actions()
        self.assertEqual(buffer.net_flow_position, -2.0)
        self.assertEqual(buffer.procure_recommended_qty, 500)
        # Set the tolerance
        buffer.company_id.ddmrp_qty_multiple_tolerance = 10.0
        # Tolerance: 10% 250 = 25, strictly needed 272 (under tolerance)
        buffer.cron_actions()
        self.assertEqual(buffer.procure_recommended_qty, 250)
        # Add more demand
        self.create_picking_out(self.product_purchased, date_move, 20)
        buffer.cron_actions()
        self.assertEqual(buffer.net_flow_position, -22.0)
        # Tolerance: 10% 250 = 25, strictly needed 294 (above tolerance)
        buffer.cron_actions()
        self.assertEqual(buffer.procure_recommended_qty, 500)

    # TEST SECTION 3: DLT, BoM's and misc

    def test_30_bom_buffer_fields(self):
        """Check if is_buffered and buffer_id are set."""
        self.assertTrue(self.bom_a.is_buffered)
        self.assertEqual(self.bom_a.buffer_id, self.buffer_a)
        product = self.productA

        # Create another buffer with a location, then change the bom location
        new_buffer = self.bufferModel.create(
            {
                "buffer_profile_id": self.buffer_profile_pur.id,
                "product_id": product.id,
                "warehouse_id": self.warehouse.id,
                "location_id": self.supplier_location.id,
                "adu_calculation_method": self.adu_fixed.id,
            }
        )
        self.bom_a.location_id = self.supplier_location.id
        self.assertTrue(self.bom_a.is_buffered)
        self.assertEqual(self.bom_a.buffer_id, new_buffer)
        new_bom = self.env["mrp.bom"].create(
            {"product_tmpl_id": product.product_tmpl_id.id}
        )
        self.assertEqual(new_bom.is_buffered, True)
        self.assertEqual(new_bom.buffer_id, self.buffer_a)

    def test_31_bom_dlt_computation(self):
        """Tests that DLT computation is correct removing buffers."""
        bom_fp01 = self.env.ref("ddmrp.mrp_bom_fp01")
        self.assertEqual(bom_fp01.dlt, 22)
        # Remove RM-01 buffer:
        orderpoint_rm01 = self.env.ref("ddmrp.stock_buffer_rm01")
        bom_line_rm01 = self.env.ref("ddmrp.mrp_bom_as01_line_rm01")
        orderpoint_rm01.active = False
        bom_line_rm01._compute_is_buffered()
        self.assertFalse(bom_line_rm01.is_buffered)
        bom_fp01._compute_dlt()
        self.assertEqual(bom_fp01.dlt, 33.0)

    def test_32_bom_dlt_computation(self):
        """Tests that DLT computation is correct adding buffers."""
        product_as01 = self.env.ref("ddmrp.product_product_as01")
        self.bufferModel.create(
            {
                "buffer_profile_id": self.buffer_profile_mmm.id,
                "product_id": product_as01.id,
                "warehouse_id": self.warehouse.id,
                "location_id": self.stock_location.id,
                "adu_calculation_method": self.adu_fixed.id,
            }
        )
        bom_fp01 = self.env.ref("ddmrp.mrp_bom_fp01")
        self.assertEqual(bom_fp01.dlt, 2.0)

    def test_33_auto_compute_nfp_off(self):
        self.main_company.ddmrp_auto_update_nfp = False
        initial_nfp = self.buffer_a.net_flow_position
        self.assertEqual(initial_nfp, 200)
        self.assertEqual(self.buffer_a.product_location_qty_available_not_res, 200)
        date_move = datetime.today()
        self.create_pickingoutA(date_move, 120)
        # NFP hasn't been updated.
        self.assertEqual(self.buffer_a.net_flow_position, initial_nfp)
        self.create_pickinginA(date_move, 35)
        # NFP hasn't been updated.
        self.assertEqual(self.buffer_a.net_flow_position, initial_nfp)
        # Update buffer, expected NFP = 200 - 120 + 35 = 115
        self.buffer_a.cron_actions()
        expected = 200 - 120 + 35
        self.assertEqual(self.buffer_a.net_flow_position, expected)

    def test_34_auto_compute_nfp_on(self):
        self.main_company.ddmrp_auto_update_nfp = True
        initial_nfp = self.buffer_a.net_flow_position
        self.assertEqual(initial_nfp, 200)
        self.assertEqual(self.buffer_a.product_location_qty_available_not_res, 200)
        date_move = datetime.today()
        self.create_pickingoutA(date_move, 120)
        # NFP has been updated after picking confirmation.
        self.assertEqual(self.buffer_a.net_flow_position, 80)
        self.create_pickinginA(date_move, 35)
        # NFP has been updated after picking confirmation.
        expected = 200 - 120 + 35
        self.assertEqual(self.buffer_a.net_flow_position, expected)

    def test_35_dlt_variants_computation(self):
        # The seller_ids attribute is the same for all variants, but correct
        # one needs to be applied when variant is specified.
        self.assertEqual(self.buffer_c_blue.dlt, 5)
        self.assertEqual(self.buffer_c_orange.dlt, 10)
        self.p_c_supinfo_orange.unlink()
        # Fall back to no-variant supplier info
        self.assertEqual(self.buffer_c_orange.dlt, 8)

    def test_36_dlt_extra_lead_time(self):
        dlt = 5
        adu = 5
        self.assertEqual(self.buffer_c_blue.dlt, dlt)
        self.assertEqual(self.buffer_c_blue.adu, adu)
        # Profile: Purchased, med, med
        previous_red = dlt * adu * 0.5 + dlt * adu * 0.5 * 0.5
        self.assertEqual(self.buffer_c_blue.red_zone_qty, previous_red)
        previous_yellow = dlt * adu
        self.assertEqual(self.buffer_c_blue.yellow_zone_qty, previous_yellow)
        previous_green = dlt * adu * 0.5
        self.assertEqual(self.buffer_c_blue.green_zone_qty, previous_green)
        # Add extra lead time.
        extra = 2
        self.buffer_c_blue.extra_lead_time = extra
        self.buffer_c_blue.cron_actions()
        self.assertEqual(self.buffer_c_blue.dlt, 5)
        new_red = (dlt + extra) * adu * 0.5 + (dlt + extra) * adu * 0.5 * 0.5
        self.assertEqual(self.buffer_c_blue.red_zone_qty, new_red)
        new_yellow = (dlt + extra) * adu
        self.assertEqual(self.buffer_c_blue.yellow_zone_qty, new_yellow)
        new_green = (dlt + extra) * adu * 0.5
        self.assertEqual(self.buffer_c_blue.green_zone_qty, new_green)

    def test_40_bokeh_charts(self):
        """Check bokeh chart computation."""
        date_move = datetime.today()
        self.create_pickingoutA(date_move, 150)
        self.create_pickinginA(date_move, 150)
        self.buffer_a.cron_actions()
        self.assertTrue(self.buffer_a.ddmrp_chart)
        self.assertTrue(self.buffer_a.ddmrp_demand_chart)
        self.assertTrue(self.buffer_a.ddmrp_supply_chart)

    def test_41_archive_template(self):
        # archive a product template:
        self.template_c.toggle_active()
        self.assertFalse(self.template_c.active)
        self.assertFalse(self.product_c_blue.active)
        self.assertFalse(self.product_c_orange.active)
        self.assertFalse(self.buffer_c_blue.active)
        self.assertFalse(self.buffer_c_orange.active)

    def test_42_archive_variant(self):
        # archive a variant
        self.product_c_blue.toggle_active()
        self.assertTrue(self.template_c.active)
        self.assertFalse(self.product_c_blue.active)
        self.assertTrue(self.product_c_orange.active)
        self.assertFalse(self.buffer_c_blue.active)
        self.assertTrue(self.buffer_c_orange.active)
        # toggle a buffer before toggling product:
        self.buffer_c_blue.toggle_active()
        self.assertTrue(self.buffer_c_blue.active)
        self.assertFalse(self.product_c_blue.active)
        self.product_c_blue.toggle_active()
        self.assertTrue(self.buffer_c_blue.active)
        self.assertTrue(self.product_c_blue.active)
