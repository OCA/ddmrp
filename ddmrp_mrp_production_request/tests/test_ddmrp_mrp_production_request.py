# Copyright 2018 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import tests


class TestDdmrpProdutionRequest(tests.SingleTransactionCase):

    def setUp(self):
        super().setUp()
        self.mr_obj = self.env['mrp.production.request']
        self.mo_obj = self.env['mrp.production']
        self.make_procurement_wiz = self.env['make.procurement.orderpoint']
        self.create_mo_wiz = self.env['mrp.production.request.create.mo']

        self.orderpoint = self.env.ref('ddmrp.stock_warehouse_orderpoint_fp01')
        self.orderpoint.product_id.mrp_production_request = True

    def _create_orderpoint_procurement(self, op, qty=10.0):
        """Make Procurement from Buffer with forced qty."""
        context = {
            'active_model': 'stock.warehouse.orderpoint',
            'active_ids': op.ids,
            'active_id': op.id
        }
        wiz = self.make_procurement_wiz.with_context(context).create({})
        wiz.item_ids.write({
            'qty': qty,
        })
        wiz.make_procurement()
        return wiz

    def _create_mo_from_mr(self, request):
        wiz = self.create_mo_wiz.with_context(
            active_ids=request.ids).create({})
        # wiz.compute_product_line_ids()
        wiz.mo_qty = 4.0
        wiz.create_mo()
        return wiz

    def test_01_mrp_request_from_buffer(self):
        """Tests creating a Manufacturing Request from a DDMRP buffer."""
        mr = self.mr_obj.search([('orderpoint_id', '=', self.orderpoint.id)])
        self.assertFalse(mr)
        self._create_orderpoint_procurement(self.orderpoint)
        mr = self.mr_obj.search([('orderpoint_id', '=', self.orderpoint.id)])
        self.assertTrue(mr)
        self.assertEqual(mr.execution_priority_level, '1_red')
        self.assertEqual(mr.on_hand_percent, 0.0)

    def test_02_mo_created_from_mr(self):
        """The buffer should be passed to the MOs created from the MR."""
        mr = self.mr_obj.search([('orderpoint_id', '=', self.orderpoint.id)])
        self._create_mo_from_mr(mr)
        mo = self.mo_obj.search([('mrp_production_request_id', '=', mr.id)])
        self.assertTrue(mo)
        self.assertEqual(mo.execution_priority_level, '1_red')
        self.assertEqual(mo.on_hand_percent, 0.0)
