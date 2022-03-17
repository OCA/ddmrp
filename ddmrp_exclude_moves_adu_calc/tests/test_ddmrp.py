# Copyright 2016-21 ForgeFlow (http://www.forgeflow.com)
# Copyright 2016 Aleph Objects, Inc. (https://www.alephobjects.com/)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from datetime import datetime, timedelta

import odoo.tests.common as common


class TestDdmrp(common.TransactionCase):
    def setUp(self):
        super().setUp()

        # Models
        self.productModel = self.env["product.product"]
        self.bufferModel = self.env["stock.buffer"]
        self.pickingModel = self.env["stock.picking"]
        self.quantModel = self.env["stock.quant"]
        self.aducalcmethodModel = self.env["product.adu.calculation.method"]
        self.locationModel = self.env["stock.location"]
        self.make_procurement_buffer_model = self.env["make.procurement.buffer"]
        self.user_model = self.env["res.users"]

        # Refs
        self.main_company = self.env.ref("base.main_company")
        self.warehouse = self.env.ref("stock.warehouse0")
        self.stock_location = self.env.ref("stock.stock_location_stock")
        self.location_shelf1 = self.env.ref("stock.stock_location_components")
        self.supplier_location = self.env.ref("stock.stock_location_suppliers")
        self.customer_location = self.env.ref("stock.stock_location_customers")
        self.uom_unit = self.env.ref("uom.product_uom_unit")
        self.buffer_profile_pur = self.env.ref(
            "ddmrp.stock_buffer_profile_replenish_purchased_short_low"
        )
        self.group_stock_manager = self.env.ref("stock.group_stock_manager")

        # Create users
        self.user = self._create_user("user_1", [self.group_stock_manager])

        self.product_a = self.productModel.create(
            {
                "name": "product A",
                "standard_price": 1,
                "type": "product",
                "uom_id": self.uom_unit.id,
                "default_code": "A",
            }
        )

        self.secondary_loc = self.locationModel.create(
            {
                "usage": "customer",
                "name": "Customer secondary location",
                "company_id": self.main_company.id,
            }
        )

        self.bin_a = self.locationModel.create(
            {
                "usage": "internal",
                "name": "Bin A",
                "location_id": self.location_shelf1.id,
                "company_id": self.main_company.id,
            }
        )

        self.bin_b = self.locationModel.create(
            {
                "usage": "internal",
                "name": "Bin B",
                "location_id": self.location_shelf1.id,
                "company_id": self.main_company.id,
            }
        )

        self.locationModel._parent_store_compute()

        self.quantModel.create(
            {
                "location_id": self.bin_a.id,
                "company_id": self.main_company.id,
                "product_id": self.product_a.id,
                "quantity": 200.0,
            }
        )
        self.quantModel.create(
            {
                "location_id": self.bin_b.id,
                "company_id": self.main_company.id,
                "product_id": self.product_a.id,
                "quantity": 200.0,
            }
        )

    def _create_user(self, login, groups):
        """Create a user."""
        group_ids = [group.id for group in groups]
        user = self.user_model.with_context(no_reset_password=True).create(
            {
                "name": "Test User",
                "login": login,
                "password": "demo",
                "email": "test@yourcompany.com",
                "groups_id": [(6, 0, group_ids)],
            }
        )
        return user

    def create_pickingout_a_customer(self, date_move, qty):
        return self.pickingModel.with_user(self.user).create(
            {
                "picking_type_id": self.ref("stock.picking_type_out"),
                "location_id": self.bin_a.id,
                "location_dest_id": self.customer_location.id,
                "scheduled_date": date_move,
                "move_lines": [
                    (
                        0,
                        0,
                        {
                            "name": "Test move",
                            "product_id": self.product_a.id,
                            "date": date_move,
                            "product_uom": self.product_a.uom_id.id,
                            "product_uom_qty": qty,
                            "location_id": self.bin_a.id,
                            "location_dest_id": self.customer_location.id,
                        },
                    )
                ],
            }
        )

    def create_pickingout_a_secondary(self, date_move, qty):
        return self.pickingModel.with_user(self.user).create(
            {
                "picking_type_id": self.ref("stock.picking_type_out"),
                "location_id": self.bin_b.id,
                "location_dest_id": self.secondary_loc.id,
                "scheduled_date": date_move,
                "move_lines": [
                    (
                        0,
                        0,
                        {
                            "name": "Test move",
                            "product_id": self.product_a.id,
                            "date": date_move,
                            "product_uom": self.product_a.uom_id.id,
                            "product_uom_qty": qty,
                            "location_id": self.bin_b.id,
                            "location_dest_id": self.customer_location.id,
                        },
                    )
                ],
            }
        )

    def _do_picking(self, picking, date):
        picking.action_confirm()
        picking.move_lines.quantity_done = picking.move_lines.product_uom_qty
        picking._action_done()
        for move in picking.move_lines:
            move.date = date

    def test_01_exclude_move_from_adu(self):
        method = self.env.ref("ddmrp.adu_calculation_method_past_120")
        buffer_a = self.bufferModel.create(
            {
                "buffer_profile_id": self.buffer_profile_pur.id,
                "product_id": self.product_a.id,
                "location_id": self.stock_location.id,
                "warehouse_id": self.warehouse.id,
                "qty_multiple": 0.0,
                "dlt": 10,
                "adu_calculation_method": method.id,
                "adu_fixed": 4,
            }
        )
        self.bufferModel.cron_ddmrp_adu()
        self.assertEqual(buffer_a.adu, 0)

        # Create, process and (it wil be ignored later):
        date_move = datetime.today() - timedelta(days=30)
        pick_excluded = self.create_pickingout_a_customer(date_move, 120)
        self._do_picking(pick_excluded, date_move)

        # Create 2 outgoing picking (towards different locations):
        date_move = datetime.today() - timedelta(days=60)
        pick_a = self.create_pickingout_a_customer(date_move, 60)
        self._do_picking(pick_a, date_move)
        pick_b = self.create_pickingout_a_secondary(date_move, 30)
        self._do_picking(pick_b, date_move)

        # Without any exclusion:
        self.bufferModel.cron_ddmrp_adu()
        to_assert_value = (120 + 60 + 30) / 120
        self.assertEqual(buffer_a.adu, to_assert_value)

        # Exclude bin B location:
        self.bin_b.exclude_from_adu = True
        self.bufferModel.cron_ddmrp_adu()
        to_assert_value = (120 + 60) / 120
        self.assertEqual(buffer_a.adu, to_assert_value)

        # Exclude specific moves:
        for move in pick_excluded.move_lines:
            move.exclude_from_adu = True
        self.bufferModel.cron_ddmrp_adu()
        to_assert_value = 60 / 120
        self.assertEqual(buffer_a.adu, to_assert_value)
