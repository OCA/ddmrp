# Copyright 2016-20 ForgeFlow S.L. (http://www.forgeflow.com)
# Copyright 2016 Aleph Objects, Inc. (https://www.alephobjects.com/)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ProductAduCalculationMethod(models.Model):
    _name = "product.adu.calculation.method"
    _description = "Product Average Daily Usage calculation method"

    @api.model
    def _get_calculation_method(self):
        return [
            ("fixed", _("Fixed ADU")),
            ("past", _("Past-looking")),
            ("future", _("Future-looking")),
            ("blended", _("Blended")),
        ]

    @api.model
    def _get_source_selection(self):
        return [
            ("actual", "Use actual Stock Moves"),
            ("estimates", "Use Demand Estimates"),
            ("estimates_mrp", "Use Demand Estimates + Indirect Demand from MRP Moves"),
        ]

    name = fields.Char(string="Name", required=True)
    method = fields.Selection(
        selection="_get_calculation_method",
        string="Calculation method",
    )
    source_past = fields.Selection(
        selection="_get_source_selection",
        string="Past Source",
        help="Information source used for past calculation.",
    )
    horizon_past = fields.Float(
        string="Past Horizon",
        help="Length-of-period horizon in days looking past.",
    )
    factor_past = fields.Float(
        string="Past Factor",
        help="When using a blended method, this is the relative weight "
        "assigned to the past part of the combination.",
        default=0.5,
    )
    source_future = fields.Selection(
        selection="_get_source_selection",
        string="Future Source",
        help="Information source used for future calculation.",
    )
    horizon_future = fields.Float(
        string="Future Horizon",
        help="Length-of-period horizon in days looking forward.",
    )
    factor_future = fields.Float(
        string="Future Factor",
        help="When using a blended method, this is the relative weight "
        "assigned to the future part of the combination.",
        default=0.5,
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
    )

    @api.constrains("method", "horizon_past", "horizon_future")
    def _check_horizon(self):
        for rec in self:
            if rec.method in ["past", "blended"] and not rec.horizon_past:
                raise ValidationError(_("Please indicate a Past Horizon."))
            if rec.method in ["blended", "future"] and not rec.horizon_future:
                raise ValidationError(_("Please indicate a Future Horizon."))

    @api.constrains("method", "source_past", "source_future")
    def _check_source(self):
        for rec in self:
            if rec.method in ["past", "blended"] and not rec.source_past:
                raise ValidationError(_("Please indicate a Past Source."))
            if rec.method in ["blended", "future"] and not rec.source_future:
                raise ValidationError(_("Please indicate a Future Source."))

    @api.constrains("method", "factor_past", "factor_future")
    def _check_factor(self):
        for rec in self.filtered(lambda r: r.method == "blended"):
            if (
                rec.factor_past + rec.factor_future != 1.0
                or rec.factor_future < 0.0
                or rec.factor_past < 0.0
            ):
                raise ValidationError(
                    _(
                        "In blended method, past and future factors must be "
                        "positive and sum exactly 1,0."
                    )
                )
