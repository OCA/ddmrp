# Copyright 2017 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


from odoo import api, fields, models


class StockWarehouseOrderpoint(models.Model):
    _inherit = 'stock.warehouse.orderpoint'

    demand_product_ids = fields.Many2many(
        comodel_name="product.product", string="Considered As Demand",
        help="This field is used for a correct product replacement within a "
             "DDMRP buffer.", readonly=True,
    )

    @api.multi
    def _past_moves_domain(self, date_from, locations):
        if not self.demand_product_ids:
            return super()._past_moves_domain(date_from, locations)
        return [('state', '=', 'done'), ('location_id', 'in', locations.ids),
                ('location_dest_id', 'not in', locations.ids),
                ('product_id', 'in', self.demand_product_ids.ids),
                ('date', '>=', date_from)]
