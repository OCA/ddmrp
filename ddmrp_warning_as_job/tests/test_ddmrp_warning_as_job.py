# Copyright 2024 ForgeFlow (https://www.camptocamp.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo.tests import tagged

from odoo.addons.ddmrp.tests.common import TestDdmrpCommon
from odoo.addons.queue_job.job import identity_exact
from odoo.addons.queue_job.tests.common import mock_with_delay


@tagged("post_install", "-at_install")
class TestDdmrpWarningAsJob(TestDdmrpCommon):
    def test_generate_ddmrp_warnings_delay_job(self):
        context = dict(self.env.context, auto_delay_ddmrp_generate_ddmrp_warnings=True)
        context.update(
            {
                "test_queue_job_no_delay": False,
            }
        )
        buffer_a = self.buffer_a.with_context(**context)

        with mock_with_delay() as (delayable_cls, delayable):
            buffer_a._generate_ddmrp_warnings()

            # check 'with_delay()' part:
            self.assertEqual(delayable_cls.call_count, 1)
            # arguments passed in 'with_delay()'
            delay_args, delay_kwargs = delayable_cls.call_args
            self.assertEqual(delay_args, (self.buffer_a,))
            self.assertEqual(delay_kwargs.get("priority"), 15)
            self.assertEqual(delay_kwargs.get("identity_key"), identity_exact)

            # check what's passed to the job method '_generate_ddmrp_warnings'
            self.assertEqual(delayable._generate_ddmrp_warnings.call_count, 1)
            delay_args, delay_kwargs = delayable._generate_ddmrp_warnings.call_args
            self.assertEqual(delay_args, ())
            self.assertDictEqual(delay_kwargs, {})
