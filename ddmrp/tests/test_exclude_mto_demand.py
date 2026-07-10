# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from datetime import datetime

from .common import TestDdmrpCommon


class TestExcludeMtoDemand(TestDdmrpCommon):
    """Make-to-order demand must not deflate the net flow position of an
    MTS buffer, mirroring the supply side which keeps MTO purchase lines out
    of the buffer."""

    def test_mto_demand_excluded_from_qualified_demand(self):
        buffer = self.buffer_purchase
        product = buffer.product_id
        qty = 30.0
        date_move = datetime.today()

        # Make-to-stock demand: a plain outgoing delivery from the buffer.
        mts_pick = self.create_picking_out(
            product, date_move, qty, source_location=self.stock_location
        )
        mts_move = mts_pick.move_ids
        self.assertFalse(mts_move._ddmrp_is_mto())

        # Make-to-order demand: an outgoing delivery pegged to a purchase line
        # (same shape and date as the MTS one). Creating the purchase line with
        # the demand move as move_dest reproduces the real MTO linkage.
        mto_pick = self.create_picking_out(
            product, date_move, qty, source_location=self.stock_location
        )
        mto_move = mto_pick.move_ids
        vendor = self.partner_model.create({"name": "MTO Vendor"})
        po = self.env["purchase.order"].create({"partner_id": vendor.id})
        pol = self.pol_model.create(
            {
                "order_id": po.id,
                "product_id": product.id,
                "name": product.display_name,
                "product_qty": qty,
                "product_uom_id": product.uom_id.id,
                "price_unit": 1.0,
                "date_planned": date_move,
                "move_dest_ids": [(6, 0, mto_move.ids)],
            }
        )

        # Both sides recognise the peg through the same relation.
        self.assertTrue(mto_move._ddmrp_is_mto())
        self.assertTrue(pol._ddmrp_is_mto())

        # Supply side: the MTO purchase line is kept out of the buffer.
        self.assertNotIn(pol, buffer.purchase_line_ids)

        # Demand side: recompute the buffer.
        self.bufferModel.cron_ddmrp(domain=[("id", "=", buffer.id)])

        # Only the MTS demand counts; the MTO demand is excluded, so the net
        # flow position is not deflated by demand served by its own supply.
        self.assertEqual(buffer.qualified_demand, qty)
        self.assertIn(mts_move, buffer.qualified_demand_stock_move_ids)
        self.assertNotIn(mto_move, buffer.qualified_demand_stock_move_ids)
