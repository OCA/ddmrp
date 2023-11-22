# Copyright 2016-20 ForgeFlow S.L. (http://www.forgeflow.com)
# Copyright 2016 Aleph Objects, Inc. (https://www.alephobjects.com/)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from datetime import datetime

import odoo.tests.common as common


class TestDdmrpCommon(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.env = cls.env(
            context=dict(
                cls.env.context,
                tracking_disable=True,
                # compatibility with ddmrp_cron_actions_as_job,
                # that would delay calls to "cron_actions" in these tests
                test_queue_job_no_delay=True,
            )
        )

        # Models
        cls.productModel = cls.env["product.product"]
        cls.templateModel = cls.env["product.template"]
        cls.bomModel = cls.env["mrp.bom"]
        cls.bomlineModel = cls.env["mrp.bom.line"]
        cls.bufferModel = cls.env["stock.buffer"]
        cls.pickingModel = cls.env["stock.picking"]
        cls.moveModel = cls.env["stock.move"]
        cls.quantModel = cls.env["stock.quant"]
        cls.estimateModel = cls.env["stock.demand.estimate"]
        cls.aducalcmethodModel = cls.env["product.adu.calculation.method"]
        cls.locationModel = cls.env["stock.location"]
        cls.make_procurement_wiz = cls.env["make.procurement.buffer"]
        cls.user_model = cls.env["res.users"]
        cls.partner_model = cls.env["res.partner"]
        cls.supinfo_model = cls.env["product.supplierinfo"]
        cls.pol_model = cls.env["purchase.order.line"]
        cls.wh_model = cls.env["stock.warehouse"]

        # Refs
        cls.main_company = cls.env.ref("base.main_company")
        cls.second_company = cls.env.ref("stock.res_company_1")
        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.warehouse2 = cls.wh_model.create(
            {
                "partner_id": cls.env.ref("base.main_partner").id,
                "name": "Warehouse 2",
                "code": "WH2",
            }
        )
        cls.warehouse_sc = cls.env.ref("stock.stock_warehouse_shop0")
        cls.stock_location = cls.env.ref("stock.stock_location_stock")
        cls.stock_location_sc = cls.warehouse_sc.lot_stock_id
        cls.location_shelf1 = cls.env.ref("stock.stock_location_components")
        cls.supplier_location = cls.env.ref("stock.stock_location_suppliers")
        cls.customer_location = cls.env.ref("stock.stock_location_customers")
        cls.inter_wh = cls.env.ref("stock.stock_location_inter_wh")
        cls.inventory_location = cls.env["stock.location"].search(
            [("usage", "=", "inventory"), ("company_id", "=", cls.main_company.id)],
            limit=1,
        )
        cls.picking_type_out = cls.env.ref("stock.picking_type_out").copy(
            {
                "reservation_method": "manual",
                "sequence_code": "DDMRP-OUT",
            }
        )
        cls.picking_type_in = cls.env.ref("stock.picking_type_in")
        cls.picking_type_internal = cls.env.ref("stock.picking_type_internal").copy(
            {
                "reservation_method": "manual",
                "sequence_code": "DDMRP-INTERNAL",
            }
        )
        cls.uom_unit = cls.env.ref("uom.product_uom_unit")
        cls.dozen_unit = cls.env.ref("uom.product_uom_dozen")
        cls.buffer_profile_pur = cls.env.ref(
            "ddmrp.stock_buffer_profile_replenish_purchased_medium_medium"
        )
        cls.buffer_profile_mmm = cls.env.ref(
            "ddmrp.stock_buffer_profile_replenish_manufactured_medium_medium"
        )
        cls.buffer_profile_distr = cls.env.ref(
            "ddmrp.stock_buffer_profile_replenish_distributed_medium_medium"
        )
        cls.buffer_profile_override = cls.env.ref(
            "ddmrp.stock_buffer_profile_replenish_override_purchased_short_low"
        )
        cls.adu_fixed = cls.env.ref("ddmrp.adu_calculation_method_fixed")
        cls.group_stock_manager = cls.env.ref("stock.group_stock_manager")
        cls.group_mrp_user = cls.env.ref("mrp.group_mrp_user")
        cls.group_change_procure_qty = cls.env.ref(
            "ddmrp.group_change_buffer_procure_qty"
        )
        cls.group_buffer_manager = cls.env.ref("ddmrp.group_stock_buffer_maintainer")
        cls.calendar = cls.env.ref("resource.resource_calendar_std")
        cls.warehouse.calendar_id = cls.calendar

        # Create users
        cls.user = cls._create_user(
            "user_1",
            [
                cls.group_stock_manager,
                cls.group_mrp_user,
                cls.group_change_procure_qty,
                cls.group_buffer_manager,
            ],
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
                "inventory_quantity": 200.0,
            }
        )
        cls.quant.action_apply_inventory()

        # Product B (purchased):
        buy_route = cls.env.ref("purchase_stock.route_warehouse0_buy")
        cls.product_purchased = cls.productModel.create(
            {
                "name": "product Purchased",
                "standard_price": 1,
                "type": "product",
                "uom_id": cls.uom_unit.id,
                "default_code": "B",
                "route_ids": [(6, 0, buy_route.ids)],
            }
        )
        cls.product_purchased_2 = cls.productModel.create(
            {
                "name": "product Purchased 2",
                "standard_price": 1,
                "type": "product",
                "uom_id": cls.uom_unit.id,
                "default_code": "B",
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

        # Product C (purchased and with variants):
        cls.template_c = cls.templateModel.create(
            {
                "name": "Product C",
                "type": "product",
                "uom_id": cls.uom_unit.id,
                "default_code": "C",
                "route_ids": [(6, 0, buy_route.ids)],
            }
        )
        cls.color_attribute = cls.env["product.attribute"].create(
            {"name": "Color", "sequence": 1}
        )
        cls.color_blue = cls.env["product.attribute.value"].create(
            {"name": "Blue", "attribute_id": cls.color_attribute.id, "sequence": 1}
        )
        cls.color_orange = cls.env["product.attribute.value"].create(
            {"name": "Orange", "attribute_id": cls.color_attribute.id, "sequence": 2}
        )
        cls.color_green = cls.env["product.attribute.value"].create(
            {"name": "Green", "attribute_id": cls.color_attribute.id, "sequence": 3}
        )
        cls.p_c_color_attribute_line = cls.env[
            "product.template.attribute.line"
        ].create(
            {
                "product_tmpl_id": cls.template_c.id,
                "attribute_id": cls.color_attribute.id,
                "value_ids": [
                    (6, 0, [cls.color_blue.id, cls.color_orange.id, cls.color_green.id])
                ],
            }
        )
        cls.product_c_blue = cls.template_c.product_variant_ids[0]
        cls.product_c_orange = cls.template_c.product_variant_ids[1]
        cls.product_c_green = cls.template_c.product_variant_ids[2]
        cls.p_c_supinfo_blue = cls.supinfo_model.create(
            {
                "product_tmpl_id": cls.template_c.id,
                "product_id": cls.product_c_blue.id,
                "name": vendor.id,
                "delay": 5.0,
            }
        )
        cls.p_c_supinfo_orange = cls.supinfo_model.create(
            {
                "product_tmpl_id": cls.template_c.id,
                "product_id": cls.product_c_orange.id,
                "name": vendor.id,
                "delay": 10.0,
            }
        )
        cls.p_c_supinfo_no_variant = cls.supinfo_model.create(
            {"product_tmpl_id": cls.template_c.id, "name": vendor.id, "delay": 8.0}
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
                "order_spike_horizon": 10.0,
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
        cls.buffer_c_blue = cls.bufferModel.create(
            {
                "buffer_profile_id": cls.buffer_profile_pur.id,
                "product_id": cls.product_c_blue.id,
                "location_id": cls.stock_location.id,
                "warehouse_id": cls.warehouse.id,
                "qty_multiple": 1.0,
                "adu_calculation_method": cls.adu_fixed.id,
                "adu_fixed": 5.0,
            }
        )
        cls.buffer_c_orange = cls.bufferModel.create(
            {
                "buffer_profile_id": cls.buffer_profile_pur.id,
                "product_id": cls.product_c_orange.id,
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
        """Create a user."""
        group_ids = [group.id for group in groups]
        user = cls.user_model.with_context(no_reset_password=True).create(
            {
                "name": "Test User",
                "login": login,
                "password": "demo",
                "email": "test@yourcompany.com",
                "groups_id": [(6, 0, group_ids)],
            }
        )
        return user

    def create_pickingoutA(self, date_move, qty, uom=False):
        if not uom:
            uom = self.productA.uom_id
        picking = self.pickingModel.with_user(self.user).create(
            {
                "picking_type_id": self.picking_type_out.id,
                "location_id": self.binA.id,
                "location_dest_id": self.customer_location.id,
                "scheduled_date": date_move,
                "move_lines": [
                    (
                        0,
                        0,
                        {
                            "name": "Test move",
                            "product_id": self.productA.id,
                            "date": date_move,
                            "product_uom": uom.id,
                            "product_uom_qty": qty,
                            "location_id": self.binA.id,
                            "location_dest_id": self.customer_location.id,
                        },
                    )
                ],
            }
        )
        picking.action_confirm()
        return picking

    def create_pickinginA(self, date_move, qty):
        picking = self.pickingModel.with_user(self.user).create(
            {
                "picking_type_id": self.picking_type_in.id,
                "location_id": self.supplier_location.id,
                "location_dest_id": self.binA.id,
                "scheduled_date": date_move,
                "move_lines": [
                    (
                        0,
                        0,
                        {
                            "name": "Test move",
                            "product_id": self.productA.id,
                            "date": date_move,
                            "date_deadline": date_move,
                            "product_uom": self.productA.uom_id.id,
                            "product_uom_qty": qty,
                            "location_id": self.supplier_location.id,
                            "location_dest_id": self.binA.id,
                        },
                    )
                ],
            }
        )
        picking.action_confirm()
        return picking

    def create_pickinginternalA(self, date_move, qty):
        picking = self.pickingModel.with_user(self.user).create(
            {
                "picking_type_id": self.picking_type_internal.id,
                "location_id": self.binA.id,
                "location_dest_id": self.binB.id,
                "scheduled_date": date_move,
                "move_lines": [
                    (
                        0,
                        0,
                        {
                            "name": "Test move",
                            "product_id": self.productA.id,
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
        picking.action_confirm()
        return picking

    def create_picking_out(self, product, date_move, qty):
        picking = self.pickingModel.with_user(self.user).create(
            {
                "picking_type_id": self.picking_type_out.id,
                "location_id": self.binA.id,
                "location_dest_id": self.customer_location.id,
                "scheduled_date": date_move,
                "move_lines": [
                    (
                        0,
                        0,
                        {
                            "name": "Test move",
                            "product_id": product.id,
                            "date": date_move,
                            "product_uom": product.uom_id.id,
                            "product_uom_qty": qty,
                            "location_id": self.binA.id,
                            "location_dest_id": self.customer_location.id,
                        },
                    )
                ],
            }
        )
        picking.action_confirm()
        return picking

    def create_picking_in(self, product, date_move, qty):
        picking = self.pickingModel.with_user(self.user).create(
            {
                "picking_type_id": self.picking_type_in.id,
                "location_id": self.supplier_location.id,
                "location_dest_id": self.binA.id,
                "scheduled_date": date_move,
                "move_lines": [
                    (
                        0,
                        0,
                        {
                            "name": "Test move",
                            "product_id": product.id,
                            "date": date_move,
                            "product_uom": product.uom_id.id,
                            "product_uom_qty": qty,
                            "location_id": self.supplier_location.id,
                            "location_dest_id": self.binA.id,
                        },
                    )
                ],
            }
        )
        picking.action_confirm()
        return picking

    def _do_picking(self, picking, date):
        """Do picking with only one move on the given date."""
        picking.action_confirm()
        picking.move_lines.quantity_done = picking.move_lines.product_uom_qty
        picking._action_done()
        for move in picking.move_lines:
            move.date = date

    def create_orderpoint_procurement(self, buffer, make_procurement=True):
        """Make Procurement from Reordering Rule"""
        wizard = (
            self.make_procurement_wiz.with_user(self.user)
            .with_context(
                active_model="stock.buffer", active_ids=buffer.ids, active_id=buffer.id
            )
            .create({})
        )
        if make_procurement:
            wizard.make_procurement()
        return wizard

    def create_inventorylossA(self, date_move, qty):
        move = self.moveModel.with_user(self.user).create(
            {
                "name": "Test inventory move",
                "product_id": self.productA.id,
                "date": date_move,
                "product_uom": self.productA.uom_id.id,
                "product_uom_qty": qty,
                "location_id": self.binA.id,
                "location_dest_id": self.inventory_location.id,
            },
        )
        return move

    def _do_move(self, move, date):
        move._action_confirm()
        move.move_line_ids.qty_done = move.move_line_ids.product_uom_qty
        move._action_done()
        move.date = date
