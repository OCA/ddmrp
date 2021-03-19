# Copyright 2016-20 ForgeFlow S.L. (http://www.forgeflow.com)
# Copyright 2016 Aleph Objects, Inc. (https://www.alephobjects.com/)
# Copyright 2018 Camptocamp SA https://www.camptocamp.com
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, models


class ProcurementGroup(models.Model):
    _inherit = "procurement.group"

    @api.model
    def _run_scheduler_tasks(self, use_new_cursor=False, company_id=False):
        """Override the standard method to disable the possibility to
        automatically procure from orderpoints and to automatically
        reserve stock moves."""
        return True

    # UOM: (stock_orderpoint_uom):
    @api.model
    def run(self, procurements, raise_user_error=True):
        Proc = self.env["procurement.group"].Procurement
        indexes_to_pop = []
        new_procs = []
        for i, procurement in enumerate(procurements):
            if "buffer_id" in procurement.values:
                buffer = procurement.values.get("buffer_id")
                if (
                    buffer.procure_uom_id
                    and procurement.product_uom != buffer.procure_uom_id
                ):
                    new_product_qty = procurement.product_uom._compute_quantity(
                        procurement.product_qty, buffer.procure_uom_id
                    )
                    new_product_uom = buffer.procure_uom_id
                    new_procs.append(
                        Proc(
                            procurement.product_id,
                            new_product_qty,
                            new_product_uom,
                            procurement.location_id,
                            procurement.name,
                            procurement.origin,
                            procurement.company_id,
                            procurement.values,
                        )
                    )
                    indexes_to_pop.append(i)
        if new_procs:
            indexes_to_pop.reverse()
            for index in indexes_to_pop:
                procurements.pop(index)
            procurements.extend(new_procs)

        return super(ProcurementGroup, self).run(procurements)
