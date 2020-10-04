# Copyright 2020 KMEE
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _


class DdmrpSimulationTotalResult(models.Model):

    _name = 'ddmrp.simulation.total.result'
    _inherit = 'ddmrp.simulation.result.mixin',
    _description = 'Ddmrp Simulation Total Result'
