# Copyright 2026 Camptocamp SA
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from datetime import datetime
from unittest.mock import patch

from odoo.tests import tagged

from odoo.addons.ddmrp.tests.common import TestDdmrpCommon
from odoo.addons.queue_job.tests.common import trap_jobs


@tagged("post_install", "-at_install")
class TestUpdateNfpJobs(TestDdmrpCommon):
    """``stock.move._update_ddmrp_nfp`` delays the buffer refresh as jobs.

    When a job only refreshes one side of the net flow position (demand or
    supply) and procures, it decides on a stale figure for the other side if
    the job refreshing that side has not run yet.
    """

    def _picking(self, picking_type, source, dest, qty, date_move):
        product = self.product_purchased
        picking_model = self.pickingModel.with_user(self.user).with_context(
            queue_job__no_delay=False
        )
        return picking_model.create(
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

    def test_buffer_fully_refreshed_when_procuring(self):
        buffer = self.buffer_purchase
        self.main_company.ddmrp_auto_update_nfp = True
        buffer.auto_procure = True
        buffer.auto_procure_option = "stockout"

        buffer.cron_actions()
        self.assertEqual(buffer.net_flow_position, 0.0)
        self.assertFalse(self._purchase_lines())

        # The receipt covers the delivery: nothing to order.
        qty = 10.0
        date_move = datetime.today()
        picking_out = self._picking(
            self.picking_type_out, self.binA, self.customer_location, qty, date_move
        )
        picking_in = self._picking(
            self.picking_type_in, self.supplier_location, self.binA, qty, date_move
        )

        # Trapped jobs only run when the test performs them.
        with trap_jobs() as trap:
            picking_out.action_confirm()
            demand_jobs = list(trap.enqueued_jobs)
            picking_in.action_confirm()
            supply_jobs = [j for j in trap.enqueued_jobs if j not in demand_jobs]

            # Run the delivery's jobs while the receipt's are pending:
            # the stored incoming quantity is still 0.
            for job in demand_jobs:
                job.perform()
            self.assertFalse(
                self._purchase_lines(),
                "replenished on a stale incoming quantity although the "
                "confirmed receipt already covers the demand",
            )

            for job in supply_jobs:
                job.perform()
            self.assertEqual(buffer.qualified_demand, qty)
            self.assertEqual(buffer.incoming_dlt_qty, qty)
            self.assertEqual(buffer.net_flow_position, 0.0)
            self.assertFalse(self._purchase_lines())

    def test_partial_refresh_without_pending_job(self):
        buffer = self.buffer_purchase
        self.main_company.ddmrp_auto_update_nfp = True
        buffer.cron_actions()
        picking_out = self._picking(
            self.picking_type_out,
            self.binA,
            self.customer_location,
            10.0,
            datetime.today(),
        )
        buffer_cls = type(buffer)
        with trap_jobs() as trap:
            picking_out.action_confirm()
            jobs = trap.enqueued_jobs
            self.assertEqual([job.kwargs for job in jobs], [{"only_nfp": "out"}])
            with patch.object(
                buffer_cls,
                "_calc_incoming_dlt_qty",
                autospec=True,
                side_effect=buffer_cls._calc_incoming_dlt_qty,
            ) as calc_incoming:
                jobs[0].perform()
        calc_incoming.assert_not_called()
        self.assertEqual(buffer.qualified_demand, 10.0)
