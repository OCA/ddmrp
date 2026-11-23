# Copyright 2020 Camptocamp (https://www.camptocamp.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import models

from odoo.addons.queue_job.job import Job, identity_exact


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
        self._patch_method(
            "_calc_adu",
            self._patch_job_auto_delay(
                "_calc_adu", context_key="auto_delay_ddmrp_calc_adu"
            ),
        )
        return super()._register_hook()

    def cron_actions(self, only_nfp=False):
        if only_nfp in ("in", "out") and self._has_pending_nfp_job(
            "out" if only_nfp == "in" else "in"
        ):
            only_nfp = False
        return super().cron_actions(only_nfp=only_nfp)

    def _has_pending_nfp_job(self, only_nfp):
        """Whether a job refreshing the other side of the net flow position
        is still waiting: procuring now would weigh a fresh figure against a
        stale one, so the refresh must cover both sides."""
        identity_key = self.cron_actions_job_options(only_nfp=only_nfp).get(
            "identity_key"
        )
        if not identity_key:
            return False
        job = Job(
            self.cron_actions, kwargs={"only_nfp": only_nfp}, identity_key=identity_key
        )
        return bool(job.job_record_with_same_identity_key())

    def cron_ddmrp(self, automatic=False, domain=None):
        return super(
            Buffer, self.with_context(auto_delay_ddmrp_cron_actions=True)
        ).cron_ddmrp(automatic=automatic, domain=domain)

    def cron_ddmrp_adu(self, automatic=False, domain=None):
        return super(
            Buffer, self.with_context(auto_delay_ddmrp_calc_adu=True)
        ).cron_ddmrp_adu(automatic=automatic, domain=domain)
