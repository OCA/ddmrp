# Copyright 2024 ForgeFlow (https://www.camptocamp.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import models

from odoo.addons.queue_job.job import identity_exact


class Buffer(models.Model):
    _inherit = "stock.buffer"

    def _generate_ddmrp_warnings_job_options(self):
        return {
            "identity_key": identity_exact,
            "priority": 15,
            "description": f"DDMRP Warning calculation ({self.display_name})",
        }

    def _register_hook(self):
        self._patch_method(
            "_generate_ddmrp_warnings",
            self._patch_job_auto_delay(
                "_generate_ddmrp_warnings",
                context_key="auto_delay_ddmrp_generate_ddmrp_warnings",
            ),
        )
        return super()._register_hook()

    def cron_generate_ddmrp_warnings(self, automatic=False):
        return super(
            Buffer, self.with_context(auto_delay_ddmrp_generate_ddmrp_warnings=True)
        ).cron_generate_ddmrp_warnings(automatic=automatic)
