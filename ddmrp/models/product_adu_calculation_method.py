# -*- coding: utf-8 -*-
# © 2016 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# © 2016 Aleph Objects, Inc. (https://www.alephobjects.com/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from datetime import timedelta
from openerp.osv import expression
from openerp import api, fields, models, _
from openerp.exceptions import Warning


class ProductAduCalculationMethod(models.Model):
    _name = 'product.adu.calculation.method'
    _description = 'Product Average Daily Usage calculation method'

    @api.model
    def _get_calculation_method(self):
        return [
            ('fixed', _('Fixed ADU')),
            ('past', _('Past-looking')),
            ('future', _('Future-looking'))]

    name = fields.Char(string="Name", required=True)

    method = fields.Selection("_get_calculation_method",
                              string="Calculation method")

    use_estimates = fields.Boolean(sting="Use estimates/forecasted values")
    horizon = fields.Float(string="Horizon",
                           help="Length-of-period horizon in days")

    company_id = fields.Many2one(
        'res.company', string='Company', required=True,
        default=lambda self:
        self.env['res.company']._company_default_get(
            'product.adu.calculation.method'))

    @api.multi
    @api.constrains('method', 'horizon')
    def _check_horizon(self):
        for rec in self:
            if rec.method in ['past', 'future'] and not rec.horizon:
                raise Warning(_('Please indicate a length-of-period horizon.'))

    @api.model
    def _compute_adu_past_demand(self, orderpoint):
        horizon = 1
        if not self.horizon:
            date_from = fields.Date.to_string(fields.date.today())

        else:
            horizon = self.horizon
            date_from = fields.Date.to_string(fields.date.today() - timedelta(
                days=self.horizon))
        date_to = fields.Date.to_string(fields.date.today())
        locations = orderpoint.location_id
        locations += self.env['stock.location'].search(
            [('id', 'child_of', [orderpoint.location_id.id])])
        if self.use_estimates:
            estimates = self.env['stock.buffer.demand.estimate'].search(
                [('location_id', 'in', locations.ids),
                 ('product_id', '=', orderpoint.product_id.id),
                 ('period_id.date_from', '>=', date_from),
                 ('period_id.date_to', '<=', date_to)])
            if estimates:
                return sum([estimate.product_uom_qty
                            for estimate in estimates]) / horizon
            else:
                return 0.0
        else:
            moves = self.env['stock.move'].search(
                [('state', '=', 'done'),
                 ('location_id', 'in', locations.ids),
                 ('product_id', '=', orderpoint.product_id.id),
                 ('date', '>=', date_from)])
            if moves:
                return sum([move.product_uom_qty for move in moves]) / horizon
            else:
                return 0.0

    @api.model
    def _compute_adu_future_demand(self, orderpoint):
        horizon = 1
        if not self.horizon:
            date_to = fields.Date.to_string(fields.date.today())

        else:
            horizon = self.horizon
            date_to = fields.Date.to_string(fields.date.today() + timedelta(
                days=self.horizon)).date()
        date_from = fields.Date.to_string(fields.date.today())
        locations = orderpoint.location_id
        locations += self.env['stock.location'].search(
            [('id', 'child_of', [orderpoint.location_id.id])])
        if self.use_estimates:
            estimates = self.env['stock.demand.estimate'].search(
                [('location_id', 'in', locations.ids),
                 ('product_id', '=', orderpoint.product_id.id),
                 ('period_id.date_from', '>=', date_from),
                 ('period_id.date_to', '<=', date_to)])
            if estimates:
                return sum([estimate.product_uom_qty
                            for estimate in estimates]) / horizon
            else:
                return 0.0
        else:
            moves = self.env['stock.move'].search(
                [('state', 'not in', ['done', 'cancel']),
                 ('location_id', 'in', locations.ids),
                 ('product_id', '=', orderpoint.product_id.id),
                 ('date', '<=', date_to)])
            if moves:
                return sum([move.product_qty for move in moves]) / horizon
            else:
                return 0.0

    @api.model
    def compute_adu(self, orderpoint):
        """Main method used to compute the ADU using the method selected.
        You can override this method when you define new calculation methods.
        """
        if self.method == 'fixed':
            return orderpoint.adu_fixed
        elif self.method == 'past':
            return self._compute_adu_past_demand(orderpoint)
        elif self.method == 'future':
            return self._compute_adu_future_demand(orderpoint)
