# Copyright 2023 ForgeFlow (http://www.forgeflow.com)

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
        self.supinfo_model = self.env["product.supplierinfo"]
        self.partner_model = self.env["res.partner"]

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

        self.product_a = self.productModel.create(
            {
                "name": "product A",
                "standard_price": 1,
                "type": "product",
                "uom_id": self.uom_unit.id,
                "default_code": "A",
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

    def create_picking(self, qty, location_id, location_dest_id):
        return self.pickingModel.create(
            {
                "picking_type_id": self.ref("stock.picking_type_out"),
                "location_id": location_id.id,
                "location_dest_id": location_dest_id.id,
                "scheduled_date": datetime.today() + timedelta(days=2),
                "move_lines": [
                    (
                        0,
                        0,
                        {
                            "name": "Test move",
                            "product_id": self.product_a.id,
                            "date": datetime.today() + timedelta(days=2),
                            "product_uom": self.product_a.uom_id.id,
                            "product_uom_qty": qty,
                            "location_id": self.bin_b.id,
                            "location_dest_id": self.customer_location.id,
                        },
                    )
                ],
            }
        )

    def test_01_exclude_location_from_ddmrp(self):
        method = self.env.ref("ddmrp.adu_calculation_method_past_120")
        buffer_a = self.bufferModel.create(
            {
                "buffer_profile_id": self.buffer_profile_pur.id,
                "product_id": self.product_a.id,
                "location_id": self.stock_location.id,
                "warehouse_id": self.warehouse.id,
                "lead_days": 10,
                "adu_calculation_method": method.id,
                "order_spike_horizon": 20,
            }
        )
        buffer_a.refresh_buffer()
        self.assertEqual(buffer_a.product_location_qty, 400)
        self.assertEqual(buffer_a.product_location_qty_available_not_res, 400)
        self.assertEqual(buffer_a.incoming_dlt_qty, 0)
        self.assertEqual(buffer_a.qualified_demand, 0)

        self.create_picking(
            120, self.bin_a, self.customer_location
        ).action_confirm()  # picking_out
        self.create_picking(
            120, self.bin_b, self.customer_location
        ).action_confirm()  # picking_out_from_exclude_location
        self.create_picking(
            120, self.supplier_location, self.bin_a
        ).action_confirm()  # picking_in
        self.create_picking(
            120, self.supplier_location, self.bin_b
        ).action_confirm()  # picking_in_to_exclude_location
        self.create_picking(
            20, self.bin_a, self.bin_b
        ).action_confirm()  # picking_internal_to_exclude_location
        self.create_picking(
            20, self.bin_b, self.bin_a
        ).action_confirm()  # picking_internal_from_exclude_location
        self.create_picking(
            5, self.bin_a, self.customer_location
        ).action_assign()  # picking_out_reserved
        self.create_picking(
            5, self.bin_b, self.customer_location
        ).action_assign()  # picking_out_reserved_from_exclude_location

        buffer_a.refresh_buffer()
        self.assertEqual(buffer_a.product_location_qty, 400)
        self.assertEqual(buffer_a.product_location_qty_available_not_res, 390)
        self.assertEqual(buffer_a.incoming_dlt_qty, 240)
        self.assertEqual(buffer_a.qualified_demand, 240)

        # Exclude bin B location:
        self.bin_b.exclude_from_ddmrp = True

        buffer_a.refresh_buffer()
        # product_location_qty from bin_a
        self.assertEqual(buffer_a.product_location_qty, 200)
        # (product_location_qty - reserved) from bin_a
        self.assertEqual(buffer_a.product_location_qty_available_not_res, 195)
        # picking_in + picking_internal_from_exclude_location
        self.assertEqual(buffer_a.incoming_dlt_qty, 140)
        # picking_out + picking_internal_to_exclude_location
        self.assertEqual(buffer_a.qualified_demand, 140)
