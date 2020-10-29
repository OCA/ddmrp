# Copyright 2020 Camptocamp (https://www.camptocamp.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).


from odoo.tests import tagged

from odoo.addons.ddmrp.tests.common import TestDdmrpCommon
from odoo.addons.queue_job.job import identity_exact
from odoo.addons.queue_job.tests.common import mock_with_delay


@tagged("post_install", "-at_install")
class TestDdmrpCronActionsAsJob(TestDdmrpCommon):
    def test_cron_actions_delay_job(self):
        context = dict(self.env.context, auto_delay_ddmrp_cron_actions=True)
        del context["test_queue_job_no_delay"]
        buffer_a = self.buffer_a.with_context(context)

        with mock_with_delay() as (delayable_cls, delayable):
            buffer_a.cron_actions(only_nfp=True)

            # check 'with_delay()' part:
            self.assertEqual(delayable_cls.call_count, 1)
            # arguments passed in 'with_delay()'
            delay_args, delay_kwargs = delayable_cls.call_args
            self.assertEqual(delay_args, (self.buffer_a,))
            self.assertEqual(delay_kwargs.get("priority"), 15)
            self.assertEqual(delay_kwargs.get("identity_key"), identity_exact)

            # check what's passed to the job method 'cron_actions'
            self.assertEqual(delayable.cron_actions.call_count, 1)
            delay_args, delay_kwargs = delayable.cron_actions.call_args
            self.assertEqual(delay_args, ())
            self.assertDictEqual(delay_kwargs, {"only_nfp": True})

    def test_calc_adu_delay_job(self):
        context = dict(self.env.context, auto_delay_ddmrp_calc_adu=True)
        del context["test_queue_job_no_delay"]
        buffer_a = self.buffer_a.with_context(context)

        with mock_with_delay() as (delayable_cls, delayable):
            buffer_a._calc_adu()

            # check 'with_delay()' part:
            self.assertEqual(delayable_cls.call_count, 1)
            # arguments passed in 'with_delay()'
            delay_args, delay_kwargs = delayable_cls.call_args
            self.assertEqual(delay_args, (self.buffer_a,))
            self.assertEqual(delay_kwargs.get("priority"), 15)
            self.assertEqual(delay_kwargs.get("identity_key"), identity_exact)

            # check what's passed to the job method '_calc_adu'
            self.assertEqual(delayable._calc_adu.call_count, 1)
            delay_args, delay_kwargs = delayable._calc_adu.call_args
            self.assertEqual(delay_args, ())
            self.assertDictEqual(delay_kwargs, {})
