# Copyright 2017-24 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class DdmrpFlowIndexGroup(models.Model):
    _name = "ddmrp.flow.index.group"

    name = fields.Char(required=True)
    summary = fields.Text()
    active = fields.Boolean(default=True)

    @api.multi
    def toggle_active(self):
        for record in self:
            record.active = not record.active
