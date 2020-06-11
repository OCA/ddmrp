# Copyright 2016-20 ForgeFlow S.L. (http://www.forgeflow.com)
# Copyright 2016 Aleph Objects, Inc. (https://www.alephobjects.com/)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from datetime import datetime

import odoo.tests.common as common


class TestDdmrpCommon(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Models
        cls.productModel = cls.env["product.product"]
        cls.bomModel = cls.env["mrp.bom"]
        cls.bomlineModel = cls.env["mrp.bom.line"]
        cls.bufferModel = cls.env["stock.buffer"]
        cls.pickingModel = cls.env["stock.picking"]
        cls.quantModel = cls.env["stock.quant"]
        cls.estimateModel = cls.env["stock.demand.estimate"]
        cls.aducalcmethodModel = cls.env["product.adu.calculation.method"]
        cls.locationModel = cls.env["stock.location"]
        cls.make_procurement_wiz = cls.env["make.procurement.buffer"]
        cls.user_model = cls.env["res.users"]
        cls.partner_model = cls.env["res.partner"]
        cls.supinfo_model = cls.env["product.supplierinfo"]
        cls.pol_model = cls.env["purchase.order.line"]

        # Refs
        cls.main_company = cls.env.ref("base.main_company")
        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.stock_location = cls.env.ref("stock.stock_location_stock")
        cls.location_shelf1 = cls.env.ref("stock.stock_location_components")
        cls.supplier_location = cls.env.ref("stock.stock_location_suppliers")
        cls.customer_location = cls.env.ref("stock.stock_location_customers")
        cls.uom_unit = cls.env.ref("uom.product_uom_unit")
        cls.buffer_profile_pur = cls.env.ref(
            "ddmrp.stock_buffer_profile_replenish_purchased_medium_medium"
        )
        cls.buffer_profile_mmm = cls.env.ref(
            "ddmrp.stock_buffer_profile_replenish_manufactured_medium_medium"
        )
        cls.adu_fixed = cls.env.ref("ddmrp.adu_calculation_method_fixed")
        cls.group_stock_manager = cls.env.ref("stock.group_stock_manager")
        cls.group_mrp_user = cls.env.ref("mrp.group_mrp_user")
        cls.group_change_procure_qty = cls.env.ref(
            "ddmrp.group_change_buffer_procure_qty"
        )
        cls.calendar = cls.env.ref("resource.resource_calendar_std")
        cls.warehouse.calendar_id = cls.calendar

        # Create users
        cls.user = cls._create_user(
            "user_1",
            [cls.group_stock_manager, cls.group_mrp_user, cls.group_change_procure_qty],
        )
        # Create Partners:
        vendor = cls.partner_model.create({"name": "Test Vendor 1"})

        # Create products and BoM's:
        manufacture_route = cls.env.ref("mrp.route_warehouse0_manufacture")
        cls.productA = cls.productModel.create(
            {
                "name": "product A",
                "standard_price": 1,
                "type": "product",
                "uom_id": cls.uom_unit.id,
                "default_code": "A",
                "route_ids": [(6, 0, manufacture_route.ids)],
                "produce_delay": 10.0,
            }
        )
        cls.component_a1 = cls.productModel.create(
            {
                "name": "Component A-1",
                "standard_price": 1,
                "type": "product",
                "uom_id": cls.uom_unit.id,
                "default_code": "RM-test01",
            }
        )
        cls.bom_a = cls.bomModel.create(
            {
                "product_tmpl_id": cls.productA.product_tmpl_id.id,
                "product_id": cls.productA.id,
            }
        )
        cls.bomlineModel.create(
            {
                "product_id": cls.component_a1.id,
                "product_qty": 2.0,
                "bom_id": cls.bom_a.id,
            }
        )
        # Create locations:
        cls.binA = cls.locationModel.create(
            {
                "usage": "internal",
                "name": "Bin A",
                "location_id": cls.location_shelf1.id,
                "company_id": cls.main_company.id,
            }
        )

        cls.binB = cls.locationModel.create(
            {
                "usage": "internal",
                "name": "Bin B",
                "location_id": cls.location_shelf1.id,
                "company_id": cls.main_company.id,
            }
        )
        cls.locationModel._parent_store_compute()

        cls.quant = cls.quantModel.create(
            {
                "location_id": cls.binA.id,
                "company_id": cls.main_company.id,
                "product_id": cls.productA.id,
                "quantity": 200.0,
            }
        )

        # Product B (purchased):
        buy_route = cls.env.ref("purchase_stock.route_warehouse0_buy")
        cls.product_purchased = cls.productModel.create(
            {
                "name": "product Purchased",
                "standard_price": 1,
                "type": "product",
                "uom_id": cls.uom_unit.id,
                "default_code": "A",
                "route_ids": [(6, 0, buy_route.ids)],
            }
        )
        cls.supinfo_model.create(
            {
                "product_tmpl_id": cls.product_purchased.product_tmpl_id.id,
                "name": vendor.id,
                "delay": 20.0,
            }
        )

        # Create buffers:
        cls.buffer_a = cls.bufferModel.create(
            {
                # TODO: this should a manufacture buffer profile. task for v14 mig.
                "buffer_profile_id": cls.buffer_profile_pur.id,
                "product_id": cls.productA.id,
                "location_id": cls.stock_location.id,
                "warehouse_id": cls.warehouse.id,
                "qty_multiple": 1.0,
                "adu_calculation_method": cls.adu_fixed.id,
                "adu_fixed": 4.0,
                "lead_days": 10.0,
            }
        )
        cls.buffer_purchase = cls.bufferModel.create(
            {
                "buffer_profile_id": cls.buffer_profile_pur.id,
                "product_id": cls.product_purchased.id,
                "location_id": cls.stock_location.id,
                "warehouse_id": cls.warehouse.id,
                "qty_multiple": 1.0,
                "adu_calculation_method": cls.adu_fixed.id,
                "adu_fixed": 5.0,
            }
        )

        # dates for a period of 120 days for estimates.
        cls.estimate_date_from = cls.calendar.plan_days(1, datetime.today()).date()
        days = 119
        dt = cls.calendar.plan_days(+1 * days + 1, datetime.today())
        cls.estimate_date_to = dt.date()

        # Run cron jobs:
        cls.bufferModel.cron_ddmrp_adu()
        cls.bufferModel.cron_ddmrp()

    @classmethod
    def _create_user(cls, login, groups):
        """ Create a user."""
        group_ids = [group.id for group in groups]
        user = cls.user_model.with_context({"no_reset_password": True}).create(
            {
                "name": "Test User",
                "login": login,
                "password": "demo",
                "email": "test@yourcompany.com",
                "groups_id": [(6, 0, group_ids)],
            }
        )
        return user

    def create_pickingoutA(self, date_move, qty):
        return self.pickingModel.with_user(self.user).create(
            {
                "picking_type_id": self.ref("stock.picking_type_out"),
                "location_id": self.binA.id,
                "location_dest_id": self.customer_location.id,
                "move_lines": [
                    (
                        0,
                        0,
                        {
                            "name": "Test move",
                            "product_id": self.productA.id,
                            "date_expected": date_move,
                            "date": date_move,
                            "product_uom": self.productA.uom_id.id,
                            "product_uom_qty": qty,
                            "location_id": self.binA.id,
                            "location_dest_id": self.customer_location.id,
                        },
                    )
                ],
            }
        )

    def create_pickinginA(self, date_move, qty):
        return self.pickingModel.with_user(self.user).create(
            {
                "picking_type_id": self.ref("stock.picking_type_in"),
                "location_id": self.supplier_location.id,
                "location_dest_id": self.binA.id,
                "move_lines": [
                    (
                        0,
                        0,
                        {
                            "name": "Test move",
                            "product_id": self.productA.id,
                            "date_expected": date_move,
                            "date": date_move,
                            "product_uom": self.productA.uom_id.id,
                            "product_uom_qty": qty,
                            "location_id": self.supplier_location.id,
                            "location_dest_id": self.binA.id,
                        },
                    )
                ],
            }
        )

    def create_pickinginternalA(self, date_move, qty):
        return self.pickingModel.with_user(self.user).create(
            {
                "picking_type_id": self.ref("stock.picking_type_internal"),
                "location_id": self.binA.id,
                "location_dest_id": self.binB.id,
                "move_lines": [
                    (
                        0,
                        0,
                        {
                            "name": "Test move",
                            "product_id": self.productA.id,
                            "date_expected": date_move,
                            "date": date_move,
                            "product_uom": self.productA.uom_id.id,
                            "product_uom_qty": qty,
                            "location_id": self.binA.id,
                            "location_dest_id": self.binB.id,
                        },
                    )
                ],
            }
        )

    def _do_picking(self, picking, date):
        """Do picking with only one move on the given date."""
        picking.action_confirm()
        picking.move_lines.quantity_done = picking.move_lines.product_uom_qty
        picking.action_done()
        for move in picking.move_lines:
            move.date = date

    def create_orderpoint_procurement(self, buffer):
        """Make Procurement from Reordering Rule"""
        context = {
            "active_model": "stock.buffer",
            "active_ids": buffer.ids,
            "active_id": buffer.id,
        }
        wizard = (
            self.make_procurement_wiz.with_user(self.user)
            .with_context(context)
            .create({})
        )
        wizard.make_procurement()
        return wizard
