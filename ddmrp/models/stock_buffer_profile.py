# -*- coding: utf-8 -*-
# © 2016 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# © 2016 Aleph Objects, Inc. (https://www.alephobjects.com/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models

_REPLENISH_METHODS = [
    ('replenish', 'Replenished'),
    ('replenish_override', 'Replenished override'),
    ('min_max', 'Min-max')
]
_ITEM_TYPES = [
    ('manufactured', 'Manufactured'),
    ('purchased', 'Purchased'),
    ('distributed', 'Distributed')
]

_LEAD_TIMES = [
    ('short', 'Short Lead Time'),
    ('medium', 'Medium'),
    ('long', 'Long')
]

_VARIABILITY = [
    ('low', 'Low'),
    ('medium', 'Medium'),
    ('high', 'High'),
]


class StockBufferProfile(models.Model):
    _name = 'stock.buffer.profile'
    _string = 'Buffer Profile'

    @api.multi
    @api.depends("item_type", "lead_time", "lead_time_factor",
                 "variability", "variability_factor")
    def _compute_name(self):
        """Get the right summary for this job."""
        for rec in self:
            rec.name = '%s %s, %s(%s), %s(%s)' % (rec.replenish_method,
                                                  rec.item_type, rec.lead_time,
                                                  rec.lead_time_factor,
                                                  rec.variability,
                                                  rec.variability_factor)

    name = fields.Char(string="Name", compute="_compute_name", store=True)
    replenish_method = fields.Selection(string="Replenishment method",
                                        selection=_REPLENISH_METHODS,
                                        required=True)
    item_type = fields.Selection(string="Item Type", selection=_ITEM_TYPES,
                                 required=True)
    lead_time = fields.Selection(string="Lead Time", selection=_LEAD_TIMES,
                                 required=True)
    lead_time_factor = fields.Float(string="Lead Time Factor")
    variability = fields.Selection(string="Variability",
                                   selection=_VARIABILITY,
                                   required=True)
    variability_factor = fields.Float(string="Variability Factor")
    company_id = fields.Many2one(
        'res.company', 'Company', required=True,
        default=lambda self: self.env['res.company']._company_default_get(
            'stock.buffer.profile'))
