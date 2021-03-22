# Copyright 2019-21 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class StockBuffer(models.Model):
    _inherit = "stock.buffer"

    demand_product_ids = fields.Many2many(
        comodel_name="product.product",
        string="Considered As Demand",
        help="This field is used for a correct product replacement within a "
        "DDMRP buffer.",
    )

    @api.constrains("demand_product_ids")
    def _check_demand_product_ids(self):
        for rec in self:
            if rec.demand_product_ids and rec.product_id not in rec.demand_product_ids:
                raise ValidationError(
                    _("Buffered product must be considered as demand.")
                )

    def _past_moves_domain(self, date_from, date_to, locations):
        if not self.demand_product_ids:
            return super()._past_moves_domain(date_from, date_to, locations)
        domain = super()._past_moves_domain(date_from, date_to, locations)
        index_replace = False
        for n, clause in enumerate(domain):
            if isinstance(clause, tuple) and clause[0] == "product_id":
                index_replace = n
        if index_replace:
            domain[index_replace] = ("product_id", "in", self.demand_product_ids.ids)
        return domain
