# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, _


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    def _get_product_search_criteria(self, bom_line):
        return [('categ_id', 'child_of', bom_line.product_id.categ_id.id)]

    def _get_product_equivalent(self, bom_line, requested_qty):
        # get all the other products in the same product category
        p_obj = self.env['product.product']
        products = p_obj.search(self._get_product_search_criteria(bom_line),
                                order='priority asc, id asc')
        # exclude the non-equivalent parts listed in the BOM line and the
        # current product
        products -= bom_line.nonequivalent_product_ids + bom_line.product_id
        product_eq = False
        for product in products:
            if product.orderpoint_ids and \
               product.orderpoint_ids[0].planning_priority_level == '3_green':
                    if product.qty_available > requested_qty:
                        product_eq = product
                        break
        return product_eq

    def _generate_raw_move(self, bom_line, line_data):
        sm = super(MrpProduction, self)._generate_raw_move(bom_line, line_data)
        if not bom_line.use_equivalences:
            return sm
        if (bom_line.orderpoint_id.planning_priority_level == '3_green' and
                bom_line.product_id.qty_available > line_data['qty']):
            return sm

        product_equivalent = self._get_product_equivalent(bom_line,
                                                          line_data['qty'])
        if product_equivalent:
            body = _('%s has been replaced by %s.' %
                     (sm.product_id.name_get()[0][1],
                      product_equivalent.name_get()[0][1]))
            sm.write({
                'price_unit': product_equivalent.standard_price,
                'product_id': product_equivalent.id,
            })
            self.message_post(body=body)
        return sm
