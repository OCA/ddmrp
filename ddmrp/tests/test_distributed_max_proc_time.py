# Copyright 2020 Camptocamp
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from freezegun import freeze_time

from odoo import fields

from .common import TestDdmrpCommon


class TestDdmrpMaxProcTime(TestDdmrpCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # we store goods in "Replenish" and make pull rules to
        # go through "Replenish Step" when we replenish Stock
        cls.replenish_location = cls.env["stock.location"].create(
            {
                "name": "Replenish",
                "location_id": cls.warehouse.view_location_id.id,
                "usage": "internal",
                "company_id": cls.main_company.id,
            }
        )
        replenish_step_location = cls.env["stock.location"].create(
            {
                "name": "Replenish Step",
                "location_id": cls.warehouse.view_location_id.id,
                "usage": "internal",
                "company_id": cls.main_company.id,
            }
        )

        replenish_route = cls.env["stock.location.route"].create(
            {"name": "Replenish", "sequence": 1}
        )
        cls.env["stock.rule"].create(
            {
                "name": "Replenish",
                "route_id": replenish_route.id,
                "location_src_id": cls.replenish_location.id,
                "location_id": replenish_step_location.id,
                "action": "pull",
                "picking_type_id": cls.warehouse.int_type_id.id,
                "procure_method": "make_to_stock",
                "warehouse_id": cls.warehouse.id,
                "company_id": cls.main_company.id,
            }
        )
        cls.env["stock.rule"].create(
            {
                "name": "Replenish Step",
                "route_id": replenish_route.id,
                "location_src_id": replenish_step_location.id,
                "location_id": cls.warehouse.lot_stock_id.id,
                "action": "pull",
                "picking_type_id": cls.warehouse.int_type_id.id,
                "procure_method": "make_to_order",
                "warehouse_id": cls.warehouse.id,
                "company_id": cls.main_company.id,
            }
        )

        # our product uses the replenishment route
        cls.product_c_orange.route_ids = replenish_route

        cls.buffer_dist = cls.bufferModel.create(
            {
                "buffer_profile_id": cls.buffer_profile_distr.id,
                "product_id": cls.product_c_orange.id,
                "location_id": cls.stock_location.id,
                "warehouse_id": cls.warehouse.id,
                "qty_multiple": 1.0,
                "adu_calculation_method": cls.adu_fixed.id,
                "adu_fixed": 5.0,
            }
        )

    @freeze_time("2020-12-10 10:00:00")
    def test_reschedule_proc_time_no_calendar(self):
        """Reschedule moves based on the proc time"""
        self.buffer_profile_distr.distributed_reschedule_max_proc_time = 180
        self.warehouse.calendar_id = False

        self.env["stock.quant"]._update_available_quantity(
            self.product_c_orange, self.replenish_location, 4000
        )
        # lie about the recommended qty to force creation of replenishment
        self.buffer_dist.procure_recommended_qty = 10000

        self.create_orderpoint_procurement(self.buffer_dist)
        moves = self.env["stock.move"].search(
            [("product_id", "=", self.product_c_orange.id)]
        )

        self.assertRecordValues(
            moves,
            [
                {"date": fields.Datetime.to_datetime("2020-12-11 13:00:00")},
                {"date": fields.Datetime.to_datetime("2020-12-11 13:00:00")},
            ],
        )

    @freeze_time("2020-12-10 10:00:00")
    def test_reschedule_proc_time_with_calendar(self):
        """Reschedule moves based on the proc time with calendar"""
        self.buffer_profile_distr.distributed_reschedule_max_proc_time = 90

        self.env["stock.quant"]._update_available_quantity(
            self.product_c_orange, self.replenish_location, 4000
        )
        # lie about the recommended qty to force creation of replenishment
        self.buffer_dist.procure_recommended_qty = 10000

        self.create_orderpoint_procurement(self.buffer_dist)
        moves = self.env["stock.move"].search(
            [("product_id", "=", self.product_c_orange.id)]
        )

        self.assertRecordValues(
            moves,
            [
                # the start of the working hours is 7:00 (UTC), should be 8:00
                # + 1:30 hour = 8:30
                {"date": fields.Datetime.to_datetime("2020-12-11 08:30:00")},
                {"date": fields.Datetime.to_datetime("2020-12-11 08:30:00")},
            ],
        )
