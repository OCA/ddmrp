# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    def _get_product_equivalent(self, bom_line, requested_qty):
        # get all the other products in the same product category
        p_obj = self.env['product.product']
        product_ids = p_obj.search([
            ('categ_id', 'child_of', bom_line.product_id.categ_id.id)],
            order='priority asc')
        # exclude the non-equivalent parts listed in the BOM line
        product_ids = product_ids - p_obj.browse(
            [p.id for p in bom_line.nonequivalent_product_ids])
        for product in product_ids:
            if product.orderpoint_ids and \
               product.orderpoint_ids[0].planning_priority_level == '3_green':
                    if product.qty_available > requested_qty:
                        break
        return product

    def _generate_raw_move(self, bom_line, line_data):
        sm = super(MrpProduction, self)._generate_raw_move(bom_line, line_data)
        if bom_line.orderpoint_id.planning_priority_level == '3_green':
            # even if it is green, check if quantity available is
            # greated than requested
            if bom_line.product_id.qty_available > line_data['qty']:
                replace_product = False
            else:
                replace_product = True
        elif not bom_line.use_equivalences:
            replace_product = False
        else:
            replace_product = True
            product_equivalent = self._get_product_equivalent(bom_line,
                                                              line_data['qty'])
        if replace_product and product_equivalent:
            # update stock move product id and  price unit
            sm.product_id = product_equivalent.id
            sm.price_unit = product_equivalent.standard_price
        return sm
