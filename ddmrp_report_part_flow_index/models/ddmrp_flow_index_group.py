# Copyright 2018 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class DdmrpFlowIndexGroup(models.Model):
    _name = 'ddmrp.flow.index.group'

    name = fields.Char('Name', required=True)
    summary = fields.Text('Summary')
    active = fields.Boolean(default=True)

    @api.multi
    def toggle_active(self):
        for record in self:
            record.active = not record.active
