# Copyright 2026 Camptocamp SA
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from datetime import datetime

from .common import TestDdmrpCommon


class TestUpdateNfpBatch(TestDdmrpCommon):
    """``stock.move._update_ddmrp_nfp`` refreshes the demand side of a buffer,
    procures, and only then refreshes its supply side.

    Confirming several moves at once (several pickings selected in the list,
    a batch, the scheduler) writes their state in one call, so one buffer can
    be on both sides of the same batch. The demand-only refresh then decides
    to procure on a supply figure that does not include the supply move of
    the very same batch.
    """

    def _picking(self, picking_type, source, dest, qty, date_move):
        """A draft picking: the helpers of the common class confirm at once,
        which is exactly what this test must not do."""
        product = self.product_purchased
        return self.pickingModel.with_user(self.user).create(
            {
                "picking_type_id": picking_type.id,
                "location_id": source.id,
                "location_dest_id": dest.id,
                "scheduled_date": date_move,
                "move_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "Test move",
                            "product_id": product.id,
                            "date": date_move,
                            "product_uom": product.uom_id.id,
                            "product_uom_qty": qty,
                            "location_id": source.id,
                            "location_dest_id": dest.id,
                        },
                    )
                ],
            }
        )

    def _purchase_lines(self):
        return self.pol_model.search([("product_id", "=", self.product_purchased.id)])

    def test_no_procurement_when_demand_and_supply_confirmed_together(self):
        buffer = self.buffer_purchase
        self.main_company.ddmrp_auto_update_nfp = True
        buffer.auto_procure = True
        buffer.auto_procure_option = "stockout"
        self.assertTrue(self.binA.is_sublocation_of(buffer.location_id))

        buffer.cron_actions()
        self.assertEqual(buffer.net_flow_position, 0.0)
        self.assertFalse(self._purchase_lines())

        qty = 10.0
        date_move = datetime.today()
        picking_out = self._picking(
            self.picking_type_out, self.binA, self.customer_location, qty, date_move
        )
        picking_in = self._picking(
            self.picking_type_in, self.supplier_location, self.binA, qty, date_move
        )
        # Draft moves do not trigger anything yet.
        self.assertFalse(self._purchase_lines())

        # One state write for both moves, so one _update_ddmrp_nfp call with
        # the buffer in out_buffers and in in_buffers.
        (picking_out | picking_in).action_confirm()

        self.assertEqual(buffer.qualified_demand, qty)
        self.assertEqual(buffer.incoming_dlt_qty, qty)
        self.assertEqual(buffer.net_flow_position, 0.0)
        self.assertFalse(
            self._purchase_lines(),
            "replenished on the demand-side refresh although the supply "
            "confirmed in the same batch already covers the demand",
        )
