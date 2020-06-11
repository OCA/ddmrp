# Copyright 2016-20 ForgeFlow S.L. (http://www.forgeflow.com)
# Copyright 2016 Aleph Objects, Inc. (https://www.alephobjects.com/)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class StockBufferProfileVariability(models.Model):
    _name = "stock.buffer.profile.variability"
    _description = "Stock Buffer Profile Variability Factor"

    name = fields.Char(string="Name", required=True)
    factor = fields.Float(string="Variability Factor", required=True)
    company_id = fields.Many2one("res.company", "Company",)
