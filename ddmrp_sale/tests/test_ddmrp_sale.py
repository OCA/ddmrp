# Copyright 2021 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from datetime import datetime as dt, timedelta as td

from odoo.addons.ddmrp.tests.common import TestDdmrpCommon


class TestDDMRPSale(TestDdmrpCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.so_model = cls.env["sale.order"]

        cls.uom_dozen = cls.env.ref("uom.product_uom_dozen")

        cls.customer = cls.partner_model.create({"name": "Customer XYZ"})
        cls.buffer_internal = cls.bufferModel.create(
            {
                "buffer_profile_id": cls.buffer_profile_mmm.id,
                "product_id": cls.productA.id,
                "location_id": cls.location_shelf1.id,
                "warehouse_id": cls.warehouse.id,
                "qty_multiple": 1.0,
                "adu_calculation_method": cls.adu_fixed.id,
                "adu_fixed": 5.0,
                "lead_days": 10.0,
                "order_spike_horizon": 10.0,
            }
        )

    @classmethod
    def _refresh_involved_buffers(cls):
        cls.buffer_a.invalidate_cache()
        cls.buffer_internal.invalidate_cache()
        cls.buffer_a.cron_actions()
        cls.buffer_internal.cron_actions()

    def test_01_can_serve_sales(self):
        self.assertTrue(self.buffer_a.can_serve_sales)
        self.assertFalse(self.buffer_internal.can_serve_sales)

    def test_02_sales_quotation_included_as_demand(self):
        self._refresh_involved_buffers()
        self.assertEqual(
            self.buffer_a.qualified_demand, self.buffer_internal.qualified_demand
        )
        so_date = dt.today() + td(days=2)
        so = self.so_model.create(
            {
                "partner_id": self.customer.id,
                "partner_invoice_id": self.customer.id,
                "partner_shipping_id": self.customer.id,
                "commitment_date": so_date,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.productA.id,
                            "name": "cool product",
                            "price_unit": 100.0,
                            "product_uom_qty": 17,  # it is a spike.
                            "commitment_date": so_date,
                        },
                    )
                ],
            }
        )
        self.assertEqual(so.state, "draft")
        self._refresh_involved_buffers()
        self.assertNotEqual(
            self.buffer_a.qualified_demand, self.buffer_internal.qualified_demand
        )
        # Buffer A sees quotations because it can serve SO's.
        diff = self.buffer_a.qualified_demand - self.buffer_internal.qualified_demand
        buffer_a_prev_nfp = self.buffer_a.net_flow_position
        self.assertEqual(diff, 17)
        so.action_confirm()
        self.assertTrue(so.picking_ids)
        self._refresh_involved_buffers()
        # After confirmation we ignore the SO and rely on the picking.
        # Check that NFP does not vary. If picking is reserved OH quantity
        # should had been reduced, if not, quantity remained as qualified demand.
        self.assertEqual(self.buffer_a.net_flow_position, buffer_a_prev_nfp)

    def test_03_sol_uom(self):
        self._refresh_involved_buffers()
        so_date = dt.today() + td(days=2)
        so = self.so_model.create(
            {
                "partner_id": self.customer.id,
                "partner_invoice_id": self.customer.id,
                "partner_shipping_id": self.customer.id,
                "commitment_date": so_date,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.productA.id,
                            "name": "cool product",
                            "price_unit": 100.0,
                            "product_uom_qty": 2,  # 2 dozens, it is a spike.
                            "product_uom": self.uom_dozen.id,
                            "commitment_date": so_date,
                        },
                    )
                ],
            }
        )
        self.assertEqual(so.state, "draft")
        self._refresh_involved_buffers()
        diff = self.buffer_a.qualified_demand - self.buffer_internal.qualified_demand
        self.assertEqual(diff, 24)
