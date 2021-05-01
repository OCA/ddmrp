# Copyright 2020 KMEE
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _


class DdmrpSimulationResultMinin(models.AbstractModel):

    _name = 'ddmrp.simulation.result.mixin'

    @api.depends('current', 'simulation')
    def _compute_percent(self):
        for record in self:
            if not record.current:
                record.percent = None
            else:
                record.percent = 100 * (record.simulation / record.current)

    code = fields.Char()
    name = fields.Char()
    current = fields.Float(
        string='Actual'
    )
    simulation = fields.Float(
        string='New/Simulated'
    )
    percent = fields.Float(
        string='Simulation / Actual (%)',
        compute='_compute_percent',
    )
    simulation_id = fields.Many2one(
        comodel_name='ddmrp.simulation',
        store=True,
    )
