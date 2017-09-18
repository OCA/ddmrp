# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
#                (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models, _
from openerp.exceptions import ValidationError

DAF_string = u"DAF"
LTF_string = u"LTF,test"  # TODO: finish this

class DdmrpAdjustmentSheet(models.TransientModel):
    _name = 'ddmrp.adjustment.sheet'
    _description = 'Buffer Adjustment Sheet'

    def _get_factors(self):
        factors = []
        if self.apply_daf:
            factors.append(DAF_string)
        if self.apply_ltf:
            factors.append(LTF_string)
        return factors

    def _prepare_line(self, period, factor):
        vals = {
            'sheet_id': self.id,
            'date_range_id': period.id,
            'factor': factor,
            'value': 0.0,
        }
        return vals

    @api.multi
    def create_lines(self):
        self.ensure_one()
        periods = self.env['date.range'].search([
            ('type_id', '=', self.date_range_type_id.id), '|',
            '&',
            ('date_start', '>=', self.date_start),
            ('date_start', '<=', self.date_end),
            '&',
            ('date_end', '>=', self.date_start),
            ('date_end', '<=', self.date_end)])
        # TODO: re-check
        domain = [('type_id', '=', self.date_range_type_id.id),
                  ('date_start', '<=', self.date_start),
                  ('date_end', '>=', self.date_start)]
        periods |= self.env['date.range'].search(
            domain)
        factors = self._get_factors()
        items = []
        for period in periods:
            for factor in factors:
                vals = self._prepare_line(period, factor)
                items.append([0, 0, vals])
        return items

    @api.multi
    @api.constrains('date_start', 'date_end')
    def _check_start_end_dates(self):
        for rec in self:
            if rec.date_start > rec.date_end:
                raise ValidationError(_(
                    'The start date cannot be later than the end date.'))

    date_start = fields.Date(
        string="Date From", required=True)
    date_end = fields.Date(
        string="Date To", required=True)
    date_range_type_id = fields.Many2one(
        string='Date Range Type', comodel_name='date.range.type',
        required=True)
    buffer_ids = fields.Many2many(
        comodel_name="stock.warehouse.orderpoint", string="DDMRP Buffers")
    line_ids = fields.Many2many(
        string="Adjustments",
        comodel_name='ddmrp.adjustment.sheet.line')
    apply_daf = fields.Boolean(string="Demand Adjustment Factor")
    apply_ltf = fields.Boolean(string="Zone Adjustment Factor, "
                                      "(not implemented yet.)") # TODO: finish this

    # HACK: https://github.com/OCA/server-tools/pull/492#issuecomment-237594285
    @api.multi
    def onchange(self, values, field_name, field_onchange):  # pragma: no cover
        if "line_ids" in field_onchange:
            for sub in ("date_range_id", "value", "factor"):
                field_onchange.setdefault("line_ids." + sub, u"")
        return super(DdmrpAdjustmentSheet, self).onchange(
            values, field_name, field_onchange)

    @api.onchange('date_range_type_id', 'date_start', 'date_end', 'apply_daf',
                  'apply_ltf')
    def _onchange_sheet(self):
        self.line_ids = [(6, 0, [])]
        lines = self.create_lines()
        self.line_ids = lines

    # TODO: validation
    @api.multi
    def button_validate(self):
        self.ensure_one()
        if not self.buffer_ids:
            raise ValidationError(_('You must select at least one buffer.'))

        if not self.line_ids.mapped('factor'):
            raise ValidationError(_('You must apply at least one factor'))
        
        res = []
        for b in self.buffer_ids:
            for line in self.line_ids:
                data = line._prepare_adjustment_data(b)
                estimate = self.env['ddmrp.adjustment'].create(
                    data)
                res.append(estimate.id)
        action = {
            'domain': [('id', 'in', res)],
            'name': _('DDMRP Buffer Adjustment'),
            'src_model': 'ddmrp.adjustment.sheet',
            'view_type': 'form',
            'view_mode': 'tree',
            'res_model': 'ddmrp.adjustment',
            'type': 'ir.actions.act_window'
        }
        return action


class DdmrpAdjustmentSheetLine(models.TransientModel):
    _name = 'ddmrp.adjustment.sheet.line'
    _description = 'Buffer Adjustment Sheet Line'

    sheet_id = fields.Many2one(comodel_name='ddmrp.adjustment.sheet')
    date_range_id = fields.Many2one(
        comodel_name='date.range', string='Period')
    factor = fields.Char(string='Factors')
    value = fields.Float(string="Value")
    
    @api.model
    def _prepare_adjustment_data(self, buf):
        data = {
            'date_range_id': self.date_range_id.id,
            'buffer_id': buf.id,
        }
        if self.factor == DAF_string:
            data['daf'] = self.value
        return data
