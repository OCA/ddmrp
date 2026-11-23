# Copyright 2020 Camptocamp (https://www.camptocamp.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

import functools

from odoo import models

from odoo.addons.queue_job.job import identity_exact


class Buffer(models.Model):
    _inherit = "stock.buffer"

    def cron_actions_job_options(self, only_nfp=False):
        return {
            "identity_key": identity_exact,
            "priority": 15,
            "description": f"DDMRP Buffer calculation ({self.display_name})",
        }

    def _calc_adu_job_options(self):
        return {
            "identity_key": identity_exact,
            "priority": 15,
            "description": f"DDMRP Buffer ADU calculation ({self.display_name})",
        }

    def _register_hook(self):
        patched = self._patch_job_auto_delay(
            "cron_actions", context_key="auto_delay_ddmrp_cron_actions"
        )
        type(self).cron_actions = functools.update_wrapper(
            patched, type(self).cron_actions
        )
        patched = self._patch_job_auto_delay(
            "_calc_adu", context_key="auto_delay_ddmrp_calc_adu"
        )
        type(self)._calc_adu = functools.update_wrapper(patched, type(self)._calc_adu)
        return super()._register_hook()

    def cron_ddmrp(self, automatic=False, domain=None):
        return super(
            Buffer, self.with_context(auto_delay_ddmrp_cron_actions=True)
        ).cron_ddmrp(automatic=automatic, domain=domain)

    def cron_ddmrp_adu(self, automatic=False, domain=None):
        return super(
            Buffer, self.with_context(auto_delay_ddmrp_calc_adu=True)
        ).cron_ddmrp_adu(automatic=automatic, domain=domain)
