# Copyright 2020 Camptocamp (https://www.camptocamp.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from .common import TestDdmrpCommon


class TestDdmrpDistributedSourceLocation(TestDdmrpCommon):
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
        cls.product_c_green.route_ids = replenish_route

        cls.buffer_dist = cls.bufferModel.create(
            {
                "buffer_profile_id": cls.buffer_profile_distr.id,
                "product_id": cls.product_c_green.id,
                "location_id": cls.stock_location.id,
                "warehouse_id": cls.warehouse.id,
                "qty_multiple": 1.0,
                "adu_calculation_method": cls.adu_fixed.id,
                "adu_fixed": 5.0,
            }
        )

        cls.buffer_profile_distr.replenish_distributed_limit_to_free_qty = True

    def test_distributed_source_location_id(self):
        # as we have a route to replenish from this location, we expect the
        # buffer to have this location set as source
        self.assertEqual(
            self.buffer_dist.distributed_source_location_id, self.replenish_location
        )
        self.assertEqual(self.buffer_dist.distributed_source_location_qty, 0)

    def test_distributed_source_location_qty(self):
        self.env["stock.quant"]._update_available_quantity(
            self.product_c_green, self.replenish_location, 4000
        )

        self.buffer_dist.invalidate_cache()
        self.assertEqual(self.buffer_dist.distributed_source_location_qty, 4000)

        self.env["stock.quant"]._update_reserved_quantity(
            self.product_c_green, self.replenish_location, 500
        )

        self.buffer_dist.invalidate_cache()
        self.assertEqual(self.buffer_dist.distributed_source_location_qty, 3500)

        self.assertEqual(
            self.env["stock.buffer"].search(
                [("distributed_source_location_qty", "=", 3500)]
            ),
            self.buffer_dist,
        )

    def _set_qty_and_create_replenish_wizard(
        self, qty_in_replenish=4000, recommended_qty=10000
    ):
        self.env["stock.quant"]._update_available_quantity(
            self.product_c_green, self.replenish_location, 4000
        )
        # lie about the recommended qty (we only want to test if the limit is
        # applied)
        self.buffer_dist.procure_recommended_qty = 10000

        return self.create_orderpoint_procurement(
            self.buffer_dist, make_procurement=False
        )

    def test_distributed_source_limit_replenish(self):
        wizard = self._set_qty_and_create_replenish_wizard()
        self.assertRecordValues(
            wizard.item_ids,
            [
                {
                    "recommended_qty": 10000,
                    # limited to the free qty
                    "qty": 4000,
                }
            ],
        )

    def test_distributed_source_limit_replenish_with_batch_limit_max(self):
        self.buffer_dist.procure_max_qty = 1200
        wizard = self._set_qty_and_create_replenish_wizard()
        self.assertRecordValues(
            wizard.item_ids,
            # we expect lines to be per batch of 1200 but maxed to the free qty
            [
                {"recommended_qty": 10000, "qty": 1200},
                {"recommended_qty": 10000, "qty": 1200},
                {"recommended_qty": 10000, "qty": 1200},
                {"recommended_qty": 10000, "qty": 400},
            ],
        )

    def test_distributed_source_limit_replenish_with_batch_limit_min(self):
        self.buffer_dist.procure_min_qty = 5000
        wizard = self._set_qty_and_create_replenish_wizard()
        self.assertRecordValues(
            wizard.item_ids,
            # the 4000 in stock is below the min of 5000, nothing moved
            [{"recommended_qty": 10000, "qty": 0}],
        )

    def test_distributed_source_limit_replenish_with_batch_limit_min_and_max(self):
        self.buffer_dist.procure_min_qty = 1000
        self.buffer_dist.procure_max_qty = 1200
        wizard = self._set_qty_and_create_replenish_wizard()
        self.assertRecordValues(
            wizard.item_ids,
            # the last batch would be 400 which is below the min limit,
            # ignore the remaining
            [
                {"recommended_qty": 10000, "qty": 1200},
                {"recommended_qty": 10000, "qty": 1200},
                {"recommended_qty": 10000, "qty": 1200},
            ],
        )

    def test_distributed_source_limit_disabled(self):
        self.buffer_profile_distr.replenish_distributed_limit_to_free_qty = False
        wizard = self._set_qty_and_create_replenish_wizard()
        self.assertRecordValues(
            wizard.item_ids,
            # normal behavior, apply the recommended qty when the option is set
            # to False on the profile
            [{"recommended_qty": 10000, "qty": 10000}],
        )
