# Copyright 2019 Camptocamp SA
# License LGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class StockLocation(models.Model):
    _inherit = "stock.location"

    # Originally added in `stock_reserve_rule` module, copying here to avoid
    # the dependency, ideally this should be in upstream stock module or a new
    # module with stock helpers at OCA.
    def is_sublocation_of(self, others):
        """Return True if self is a sublocation of at least one other"""
        self.ensure_one()
        # Efficient way to verify that the current location is
        # below one of the other location without using SQL.
        return any(self.parent_path.startswith(other.parent_path) for other in others)
