# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models, _


class DdmrpProductReplace(models.TransientModel):
    _name = "ddmrp.product.replace"

    @api.multi
    @api.depends("old_product_id")
    def _compute_orderpoint_ids(self):
        for rec in self:
            rec.orderpoint_ids = self.env['stock.warehouse.orderpoint'].search([
                ('product_id', '=', rec.old_product_id.id)])

    old_product_id = fields.Many2one(
        comodel_name="product.product", string="Replaced Product",
        help="Product to be replaced.", required=True, ondelete="cascade",
    )
    orderpoint_ids = fields.Many2many(
        comodel_name="stock.warehouse.orderpoint",
        string="Affected Buffers",
        readonly=True, compute="_compute_orderpoint_ids",
    )
    new_product_id = fields.Many2one(
        comodel_name="product.product", string="Substitute Product",
        help="Product that is going to replace the other one.",
    )
    use_existing = fields.Selection(
        string="Use Existing/New Product", required=True,
        selection=[("existing", "Use Existing Product"),
                   ("new", "Create New Product")],
    )
    new_product_name = fields.Char(string="New Product Name")
    new_product_default_code = fields.Char(string="New Product Internal Ref.")
    copy_route = fields.Boolean(string="Copy Routes")
    copy_putaway = fields.Boolean(string="Copy Put Away Strategy")
    consider_past_demand = fields.Boolean(
        string="Consider Old Product Demand",
        help="Consider Old product moves as demand for new product",
        default=True,
    )

    @api.multi
    def button_validate(self):
        self.ensure_one()
        if self.use_existing == 'new':
            default = dict(
                name=self.new_product_name,
                default_code=self.new_product_default_code,
            )
            if not self.copy_route:
                default['route_ids'] = None
            if (self.copy_putaway and (
                    self.old_product_id.product_putaway_ids or
                    self.old_product_id.product_tmpl_id.product_putaway_ids)):
                default['product_putaway_ids'] = [
                    (6, 0, self.old_product_id.product_putaway_ids.ids or
                     self.old_product_id.product_tmpl_id.
                     product_putaway_ids.ids)]
            self.new_product_id = self.old_product_id.copy(
                default=default)
        elif self.use_existing == 'existing':
            if self.copy_route:
                self.new_product_id.write({
                    'route_ids': [(6, 0, self.old_product_id.route_ids.ids)],
                })
            if (self.copy_putaway and (
                    self.old_product_id.product_putaway_ids or
                    self.old_product_id.product_tmpl_id.product_putaway_ids)):
                self.new_product_id.write({
                    'product_putaway_ids': [
                        (6, 0, self.old_product_id.product_putaway_ids.ids or
                         self.old_product_id.product_tmpl_id.
                         product_putaway_ids.ids)],
                })
        if self.orderpoint_ids:
            vals = {
                'product_id': self.new_product_id.id,
            }
            if self.consider_past_demand:
                vals['demand_product_ids'] = [
                    (6, 0, (self.old_product_id + self.new_product_id).ids)]
            self.orderpoint_ids.write(vals)
        return {
            'name': _('Replacing Product'),
            'res_id': self.new_product_id.id,
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'product.product',
            'type': 'ir.actions.act_window'
        }
