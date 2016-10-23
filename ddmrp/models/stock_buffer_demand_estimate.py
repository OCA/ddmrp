# -*- coding: utf-8 -*-
# © 2016 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# © 2016 Aleph Objects, Inc. (https://www.alephobjects.com/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models, _
import openerp.addons.decimal_precision as dp


class StockBufferDemandEstimate(models.Model):
    _name = 'stock.buffer.demand.estimate'
    _description = 'Stock Buffer Demand Estimate Line'

    @api.one
    @api.depends('product_id', 'product_uom', 'product_uom_qty')
    def _compute_product_qty(self):
        if self.product_uom:
            self.product_qty = self.product_uom._compute_quantity(
                self.product_uom_qty, self.product_id.uom_id)

    period_id = fields.Many2one(
        comodel_name="stock.buffer.demand.estimate.period",
        string="Estimating Period",
        required=True)
    buffer_id = fields.Many2one(comodel_name="stock.warehouse.orderpoint",
                                string="Stock Buffer")
    product_id = fields.Many2one(comodel_name="product.product",
                                 string="Product",
                                 related="buffer_id.product_id")
    product_uom = fields.Many2one(comodel_name="product.uom",
                                  string="Product",
                                  related="buffer_id.product_uom")
    location_id = fields.Many2one(comodel_name="stock.location",
                                  string="Location",
                                  related="buffer_id.location_id")
    warehouse_id = fields.Many2one(comodel_name="stock.warehouse",
                                   string="Warehouse",
                                   related="buffer_id.warehouse_id")
    product_uom_qty = fields.Float(
        string="Quantity",
        digits_compute=dp.get_precision('Product Unit of Measure'))
    company_id = fields.Many2one(
        comodel_name='res.company', string='Company', required=True,
        default=lambda self: self.env['res.company']._company_default_get(
            'stock.buffer.demand.estimate'))

    @api.multi
    def name_get(self):
        res = []
        for rec in self:
            name = "%s - %s" % (rec.period_id.name, rec.buffer_id.name)
            res.append((rec.id, name))
        return res
