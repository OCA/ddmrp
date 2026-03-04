# Copyright 2026 ForgeFlow S.L. (http://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class StockBuffer(models.Model):
    _inherit = "stock.buffer"

    def _get_unconfirmed_po_states(self):
        return super()._get_unconfirmed_po_states() + ("approved",)
