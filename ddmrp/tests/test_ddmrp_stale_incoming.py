# Copyright 2026 Camptocamp SA
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from datetime import datetime

from .common import TestDdmrpCommon


class TestDdmrpStaleIncoming(TestDdmrpCommon):
    """Reproduce the duplicate replenishment caused by a stale supply side.

    ``cron_actions(only_nfp="out")`` refreshes the demand side only, but it
    still recomputes the net flow position and still calls ``do_auto_procure``.
    The net flow position is therefore computed with the ``incoming_dlt_qty``
    value stored by the previous full refresh. When a supply was created in
    between, that stored value is too low and the buffer replenishes a second
    time.
    """

    def test_auto_procure_with_stale_incoming_qty(self):
        buffer = self.buffer_purchase
        date_move = datetime.today()
        self.main_company.ddmrp_auto_update_nfp = True

        # 1. Full refresh, as the nightly cron does. There is no supply yet, so
        #    the supply side is stored as 0.
        buffer.cron_actions()
        self.assertEqual(buffer.incoming_dlt_qty, 0.0)
        self.assertGreater(buffer.top_of_green, 0.0)

        # 2. A supply covering the whole buffer is created. The supply side
        #    refresh does not happen: in production it is an asynchronous queue
        #    job, and the demand side refresh of step 3 can run before it.
        supply_qty = buffer.top_of_green
        self.main_company.ddmrp_auto_update_nfp = False
        self.create_picking_in(self.product_purchased, date_move, supply_qty)
        self.main_company.ddmrp_auto_update_nfp = True

        # 3. Something on the demand side triggers a demand-only refresh.
        buffer.auto_procure = True
        buffer.auto_procure_option = "standard"
        buffer.cron_actions(only_nfp="out")

        # The buffer is already fully covered by the supply of step 2, so it
        # must not procure anything.
        pol = self.pol_model.search([("product_id", "=", self.product_purchased.id)])
        self.assertFalse(
            pol,
            "The buffer replenished a second time although the pending supply "
            "already covers it.",
        )
        self.assertEqual(buffer.net_flow_position, supply_qty)
