# Copyright 2021-26 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from datetime import datetime as dt, timedelta as td
from unittest.mock import patch

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
        cls.buffer_a.invalidate_recordset()
        cls.buffer_internal.invalidate_recordset()
        cls.buffer_a.cron_actions()
        cls.buffer_internal.cron_actions()

    def test_01_can_serve_sales(self):
        self.assertTrue(self.buffer_a.can_serve_sales)
        self.assertFalse(self.buffer_internal.can_serve_sales)
        self.warehouse.delivery_steps = "pick_pack_ship"
        self.buffer_a._compute_can_serve_sales()
        self.assertTrue(self.buffer_a.can_serve_sales)

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
                        },
                    )
                ],
            }
        )
        self.assertEqual(so.state, "draft")
        self._refresh_involved_buffers()
        diff = self.buffer_a.qualified_demand - self.buffer_internal.qualified_demand
        self.assertEqual(diff, 24)

    def test_04_sales_quotation_canceled_included_as_demand(self):
        """
        The quotation is canceled and therefore its stock.moves canceled, so we can take
        into account the quotation if it's set as draft again.

        You cannot cancel a sale order if it has done moves.
        """
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
        self.assertEqual(diff, 17)
        so.action_confirm()
        self.assertTrue(so.order_line.move_ids)
        self._refresh_involved_buffers()
        self.assertEqual(
            self.buffer_a.qualified_demand, self.buffer_internal.qualified_demand
        )
        so._action_cancel()
        so.action_draft()
        self.assertEqual(so.state, "draft")
        self._refresh_involved_buffers()
        self.assertNotEqual(
            self.buffer_a.qualified_demand, self.buffer_internal.qualified_demand
        )
        diff = self.buffer_a.qualified_demand - self.buffer_internal.qualified_demand
        buffer_a_prev_nfp = self.buffer_a.net_flow_position
        buffer_internal_prev_nfp = self.buffer_internal.net_flow_position
        self.assertEqual(diff, 17)
        so.action_confirm()
        self.assertTrue(so.picking_ids)
        self._refresh_involved_buffers()
        self.assertEqual(self.buffer_a.net_flow_position, buffer_a_prev_nfp)
        self.assertEqual(
            buffer_internal_prev_nfp - self.buffer_internal.net_flow_position, 17
        )

    def _create_so(self, qty, uom=None):
        line_vals = {
            "product_id": self.productA.id,
            "name": "cool product",
            "price_unit": 100.0,
            "product_uom_qty": qty,
        }
        if uom:
            line_vals["product_uom"] = uom.id
        return self.so_model.create(
            {
                "partner_id": self.customer.id,
                "partner_invoice_id": self.customer.id,
                "partner_shipping_id": self.customer.id,
                "commitment_date": dt.today() + td(days=2),
                "order_line": [(0, 0, line_vals)],
            }
        )

    def _skip_stock_rule(self):
        return patch.object(
            type(self.env["sale.order.line"]),
            "_action_launch_stock_rule",
            return_value=True,
        )

    def _get_qualified_demand_diff(self):
        self._refresh_involved_buffers()
        return self.buffer_a.qualified_demand - self.buffer_internal.qualified_demand

    def test_05_confirmed_without_moves_included_as_demand(self):
        self.assertAlmostEqual(self._get_qualified_demand_diff(), 0)
        so = self._create_so(17)
        with self._skip_stock_rule():
            so.action_confirm()
        self.assertEqual(so.state, "sale")
        self.assertFalse(so.order_line.move_ids)
        self.assertAlmostEqual(self._get_qualified_demand_diff(), 17)
        self.assertIn(so.order_line, self.buffer_a.qualified_demand_sale_order_line_ids)
        buffer_a_prev_nfp = self.buffer_a.net_flow_position
        so.order_line._action_launch_stock_rule()
        self.assertTrue(so.picking_ids)
        self._refresh_involved_buffers()
        self.assertNotIn(
            so.order_line, self.buffer_a.qualified_demand_sale_order_line_ids
        )
        self.assertEqual(self.buffer_a.net_flow_position, buffer_a_prev_nfp)

    def test_06_confirmed_partially_covered(self):
        so = self._create_so(2, uom=self.uom_dozen)
        so.action_confirm()
        self.assertAlmostEqual(self._get_qualified_demand_diff(), 0)
        with self._skip_stock_rule():
            so.order_line.product_uom_qty = 4
        self.assertAlmostEqual(self._get_qualified_demand_diff(), 24)

    def test_07_locked_order_not_included_as_demand(self):
        so = self._create_so(17)
        with self._skip_stock_rule():
            so.action_confirm()
        so.action_done()
        self.assertEqual(so.state, "done")
        self.assertAlmostEqual(self._get_qualified_demand_diff(), 0)
