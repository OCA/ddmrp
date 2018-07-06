# Copyright 2018 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class StockWarehouse(models.Model):
    _inherit = 'stock.warehouse'

    nfp_incoming_safety_factor = fields.Float(
        'Net Flow Position Incoming Safety Factor',
        help='Factor used to compute the number of days to look into the '
             'future for incoming shipments for the purposes of the Net '
             'Flow position calculation.')
