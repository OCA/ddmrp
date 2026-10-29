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
        self._patch_method(
            "cron_actions",
            self._patch_job_auto_delay(
                "cron_actions", context_key="auto_delay_ddmrp_cron_actions"
            ),
        )
        # Patch _patch_job_auto_delay to control the job key
        # every job gets the same arguments, hence the same identity key.
        self._patch_method("cron_actions", self._patch_cron_actions_full_nfp())

        self._patch_method(
            "_calc_adu",
            self._patch_job_auto_delay(
                "_calc_adu", context_key="auto_delay_ddmrp_calc_adu"
            ),
        )
        return super()._register_hook()

    def _patch_cron_actions_full_nfp(self):
        """Never delay a partial refresh: each job procures, so procuring
        after refreshing only the demand or only the supply would weigh a
        fresh figure against a stale one, whatever the order of the jobs.
        """

        def full_nfp_wrapper(self, only_nfp=False):
            if self.env.context.get("auto_delay_ddmrp_cron_actions"):
                only_nfp = False
            return full_nfp_wrapper.origin(self, only_nfp=only_nfp)

        return functools.update_wrapper(full_nfp_wrapper, self.cron_actions)

    def cron_ddmrp(self, automatic=False, domain=None):
        return super(
            Buffer, self.with_context(auto_delay_ddmrp_cron_actions=True)
        ).cron_ddmrp(automatic=automatic, domain=domain)

    def cron_ddmrp_adu(self, automatic=False, domain=None):
        return super(
            Buffer, self.with_context(auto_delay_ddmrp_calc_adu=True)
        ).cron_ddmrp_adu(automatic=automatic, domain=domain)
