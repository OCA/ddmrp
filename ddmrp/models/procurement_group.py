# Copyright 2016-18 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# Copyright 2016 Aleph Objects, Inc. (https://www.alephobjects.com/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
# Copyright 2018 Camptocamp SA https://www.camptocamp.com

from odoo import api, models


class ProcurementGroup(models.Model):
    _inherit = 'procurement.group'

    @api.model
    def _procure_orderpoint_confirm(self, use_new_cursor=False,
                                    company_id=False):
        """ Override the standard method to disable the possibility to
        automatically create procurements based on order points.
        With DDMRP it is in the hands of the planner to manually
        create procurements, based on the procure recommendations."""
        return {}
