# Copyright 2021 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo.addons.ddmrp.tests.common import TestDdmrpCommon


class TestDDMRPWarning(TestDdmrpCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.warning_item_model = cls.env["ddmrp.warning.item"]
        cls.spike_warning = cls.env.ref(
            "ddmrp_warning.ddmrp_warning_definition_dlt_and_spike_horizon"
        )

        cls.buffer_warnings = cls.bufferModel.create(
            {
                "buffer_profile_id": cls.buffer_profile_mmm.id,
                "product_id": cls.productA.id,
                "location_id": cls.location_shelf1.id,
                "warehouse_id": cls.warehouse.id,
                "qty_multiple": 1.0,
                "adu_calculation_method": cls.adu_fixed.id,
                "adu_fixed": 5.0,
                "lead_days": 10.0,
                "order_spike_horizon": 0.0,
            }
        )

    @classmethod
    def _refresh_involved_buffers(cls):
        cls.buffer_warnings.cron_actions()
        cls.buffer_warnings._generate_ddmrp_warnings()

    def test_01_buffer_with_warnings(self):
        self._refresh_involved_buffers()
        self.assertTrue(self.buffer_warnings.ddmrp_warning_item_ids)
        prev_count = len(self.buffer_warnings.ddmrp_warning_item_ids)
        spike_warning_item = self.buffer_warnings.ddmrp_warning_item_ids.filtered(
            lambda w: w.warning_definition_id == self.spike_warning
        )
        self.assertTrue(spike_warning_item)
        # Fix issue:
        self.buffer_warnings.write({"order_spike_horizon": 10.0})
        self._refresh_involved_buffers()
        new_count = len(self.buffer_warnings.ddmrp_warning_item_ids)
        self.assertEqual(prev_count - new_count, 1)
