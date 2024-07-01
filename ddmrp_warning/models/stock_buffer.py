# Copyright 2021 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

import logging
import threading

from odoo import api, fields, models
from odoo.tools.misc import split_every

_logger = logging.getLogger(__name__)


class Buffer(models.Model):
    _inherit = "stock.buffer"

    ddmrp_warning_item_ids = fields.One2many(
        comodel_name="ddmrp.warning.item",
        inverse_name="buffer_id",
        readonly=True,
    )

    def _generate_ddmrp_warnings(self):
        definitions = self.env["ddmrp.warning.definition"].search([])
        item_model = self.env["ddmrp.warning.item"]
        for rec in self:
            for d in definitions:
                existing = item_model.search(
                    [("buffer_id", "=", rec.id), ("warning_definition_id", "=", d.id)]
                )
                warning_applicable = d._is_warning_applicable(rec)
                if warning_applicable:
                    warning_raised = d.evaluate_definition(rec)
                    if warning_raised and not existing:
                        item_model.create(
                            {"buffer_id": rec.id, "warning_definition_id": d.id}
                        )
                    elif not warning_raised and existing:
                        existing.unlink()
                elif not warning_applicable and existing:
                    existing.unlink()

    def action_generate_warnings(self):
        self._generate_ddmrp_warnings()
        return True

    @api.model
    def cron_generate_ddmrp_warnings(self, automatic=False):
        auto_commit = not getattr(threading.current_thread(), "testing", False)
        buffer_ids = self.search([]).ids
        i = 0
        j = len(buffer_ids)
        for buffer_chunk_ids in split_every(self.CRON_DDMRP_CHUNKS, buffer_ids):
            for b in self.browse(buffer_chunk_ids).exists():
                try:
                    i += 1
                    _logger.debug(
                        f"ddmrp cron_generate_ddmrp_warnings: {b.name}. ({i}/{j})"
                    )
                    if automatic:
                        with self.env.cr.savepoint():
                            b._generate_ddmrp_warnings()
                    else:
                        b._generate_ddmrp_warnings()
                except Exception:
                    _logger.exception("Fail to compute Warnings for buffer %s", b.name)
                    if not automatic:
                        raise
            if auto_commit:
                self._cr.commit()  # pylint: disable=E8102
        return True
