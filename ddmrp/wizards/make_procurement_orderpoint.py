# Copyright 2018 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class MakeProcurementOrderpoint(models.TransientModel):
    _inherit = 'make.procurement.orderpoint'

    @api.multi
    def make_procurement(self):
        res = super().make_procurement()
        orderpoints = self.mapped('item_ids.orderpoint_id')
        self.env.add_todo(
            orderpoints._fields['procure_recommended_qty'], orderpoints)
        orderpoints.recompute()
        return res
