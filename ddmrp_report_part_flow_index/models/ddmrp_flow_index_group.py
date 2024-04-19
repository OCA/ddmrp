# Copyright 2017-24 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class DdmrpFlowIndexGroup(models.Model):
    _name = "ddmrp.flow.index.group"
    _order = "sequence, id"

    name = fields.Char(required=True)
    summary = fields.Text()
    active = fields.Boolean(default=True)
    lower_range = fields.Float(help="Lower range used to assign in stock buffer")
    upper_range = fields.Float(help="Upper range used to assign in stock buffer")
    sequence = fields.Integer(required=True)

    def toggle_active(self):
        for record in self:
            record.active = not record.active
