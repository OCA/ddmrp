# Copyright 2018 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class MultiLevelMrp(models.TransientModel):
    _inherit = 'mrp.multi.level'

    @api.model
    def _exclude_from_mrp(self, mrp_area, product):
        """ Exclude from MRP scheduler products that are buffered. """
        res = super(MultiLevelMrp, self)._exclude_from_mrp(mrp_area, product)
        ddmrp = self.env['stock.warehouse.orderpoint'].search([
            ('location_id', '=', mrp_area.location_id.id),  # child of?
            ('product_id', '=', product.id),
            ('buffer_profile_id', '!=', False),
        ])
        if ddmrp:
            return True
        return res
