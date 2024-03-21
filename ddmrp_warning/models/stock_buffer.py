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

    ddmrp_warning_definition_name = fields.Char(
        compute="_compute_ddmrp_warning_definition_name",
        search="_search_ddmrp_warning_definition_name",
    )

    has_high_ddmrp_warnings = fields.Boolean(
        compute="_compute_has_ddmrp_warnings",
        search="_search_has_high_ddmrp_warnings",
    )

    has_medium_ddmrp_warnings = fields.Boolean(
        compute="_compute_has_ddmrp_warnings",
        search="_search_has_medium_ddmrp_warnings",
    )

    has_low_ddmrp_warnings = fields.Boolean(
        compute="_compute_has_ddmrp_warnings",
        search="_search_has_low_ddmrp_warnings",
    )

    @api.depends("ddmrp_warning_item_ids")
    def _compute_ddmrp_warning_definition_name(self):
        for rec in self:
            rec.ddmrp_warning_definition_name = ""
            for item in rec.ddmrp_warning_item_ids:
                rec.ddmrp_warning_definition_name += (
                    item.warning_definition_id.name + ","
                )

    @api.depends("ddmrp_warning_item_ids")
    def _compute_has_high_ddmrp_warnings(self):
        for rec in self:
            rec.has_high_ddmrp_warnings = False
            rec.has_medium_ddmrp_warnings = False
            rec.has_low_ddmrp_warnings = False

            severities = rec.ddmrp_warning_item_ids.mapped("severity")
            if "3_high" in severities:
                rec.has_high_ddmrp_warnings = True
            if "2_mid" in severities:
                rec.has_medium_ddmrp_warnings = True
            if "1_low" in severities:
                rec.has_low_ddmrp_warnings = True

    @api.model
    def _search_ddmrp_warning_definition_name(self, operator, value):
        buffers = self.search([("ddmrp_warning_item_ids", "!=", [])])
        buffers_filtered = buffers.filtered(
            lambda b: value
            in " ".join(b.ddmrp_warning_item_ids.warning_definition_id.mapped("name"))
        )
        if value:
            return [("id", "in", buffers_filtered.ids)]
        else:
            return [("id", "not in", buffers_filtered.ids)]

    @api.model
    def _search_has_high_ddmrp_warnings(self, operator, value):
        buffers = self.search([("ddmrp_warning_item_ids", "!=", [])])
        buffers_high = buffers.filtered(
            lambda b: "3_high" in b.ddmrp_warning_item_ids.mapped("severity")
        )
        if value:
            return [("id", "in", buffers_high.ids)]
        else:
            return [("id", "not in", buffers_high.ids)]

    @api.model
    def _search_has_medium_ddmrp_warnings(self, operator, value):
        buffers = self.search([("ddmrp_warning_item_ids", "!=", [])])
        buffers_medium = buffers.filtered(
            lambda b: "2_mid" in b.ddmrp_warning_item_ids.mapped("severity")
        )
        if value:
            return [("id", "in", buffers_medium.ids)]
        else:
            return [("id", "not in", buffers_medium.ids)]

    @api.model
    def _search_has_low_ddmrp_warnings(self, operator, value):
        buffers = self.search([("ddmrp_warning_item_ids", "!=", [])])
        buffers_low = buffers.filtered(
            lambda b: "1_low" in b.ddmrp_warning_item_ids.mapped("severity")
        )
        if value:
            return [("id", "in", buffers_low.ids)]
        else:
            return [("id", "not in", buffers_low.ids)]

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
                        "ddmrp cron_generate_ddmrp_warnings: {}. ({}/{})".format(
                            b.name, i, j
                        )
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
