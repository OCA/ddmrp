# Copyright 2019-20 ForgeFlow S.L. (http://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_compare


class MakeProcurementBuffer(models.TransientModel):
    _name = "make.procurement.buffer"
    _description = "Make Procurements from Stock Buffers"

    partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Vendor",
        help="If set, will be used as preferred vendor for purchase routes.",
    )
    item_ids = fields.One2many(
        comodel_name="make.procurement.buffer.item",
        inverse_name="wiz_id",
        string="Items",
    )

    @api.model
    def _prepare_item(self, buffer, qty_override=None):
        qty = (
            qty_override if qty_override is not None else buffer.procure_recommended_qty
        )
        return {
            "recommended_qty": buffer.procure_recommended_qty,
            "qty": qty,
            "uom_id": buffer.procure_uom_id.id or buffer.product_uom.id,
            "date_planned": buffer._get_date_planned(),
            "buffer_id": buffer.id,
            "product_id": buffer.product_id.id,
            "warehouse_id": buffer.warehouse_id.id,
            "location_id": buffer.location_id.id,
        }

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        buffer_obj = self.env["stock.buffer"]
        buffer_ids = self.env.context["active_ids"] or []
        active_model = self.env.context["active_model"]

        if not buffer_ids:
            return res
        assert active_model == "stock.buffer", "Bad context propagation"

        items = []
        for line in buffer_obj.browse(buffer_ids):
            max_order = line.procure_max_qty
            qty_to_order = line._procure_qty_to_order()

            if max_order and max_order < qty_to_order:
                # split the procurement in batches:
                while qty_to_order > 0.0:
                    if qty_to_order > max_order:
                        qty = max_order
                    else:
                        rounding = (
                            line.procure_uom_id.rounding or line.product_uom.rounding
                        )
                        profile = line.buffer_profile_id
                        limit_to_free_qty = (
                            line.item_type == "distributed"
                            and profile.replenish_distributed_limit_to_free_qty
                        )
                        if limit_to_free_qty:
                            if (
                                float_compare(
                                    qty_to_order,
                                    line.procure_min_qty,
                                    precision_rounding=rounding,
                                )
                                < 0
                            ):
                                # not enough in stock to have a batch
                                # respecting the min qty!
                                break
                            # not more that what we have in stock!
                            qty = qty_to_order
                        else:
                            # FIXME it will apply a second time the unit conversion
                            qty = line._adjust_procure_qty(qty_to_order)
                    items.append([0, 0, self._prepare_item(line, qty)])
                    qty_to_order -= qty
            else:
                items.append([0, 0, self._prepare_item(line, qty_to_order)])
        res["item_ids"] = items
        return res

    def _get_procurement_location(self, item):
        return item.buffer_id.location_id

    def _get_procurement_name(self, item):
        return item.buffer_id.name

    def _get_procurement_origin(self, item):
        return item.buffer_id.name

    def make_procurement(self):
        self.ensure_one()
        errors = []
        pg_obj = self.env["procurement.group"]
        procurements = []
        for item in self.item_ids:
            # As procurement is processed with SUPERUSER_ID (see _run_buy and
            # _run_manufacture), ensure the current user has write access on
            # the buffer to make a procurement. Otherwise, any user can request
            # a procurement on any buffer
            item.buffer_id.check_access_rights("write")
            item.buffer_id.check_access_rule("write")
            if item.qty <= 0.0:
                raise ValidationError(_("Quantity must be positive."))
            if not item.buffer_id:
                raise ValidationError(_("No stock buffer found."))
            values = item._prepare_values_make_procurement()
            proc_location = self._get_procurement_location(item)
            proc_name = self._get_procurement_name(item)
            proc_origin = self._get_procurement_origin(item)
            procurements.append(
                pg_obj.Procurement(
                    item.buffer_id.product_id,
                    item.qty,
                    item.uom_id,
                    proc_location,
                    proc_name,
                    proc_origin,
                    item.buffer_id.company_id,
                    values,
                )
            )
        # Run procurements
        try:
            pg_obj.run(procurements)
        except UserError as error:
            errors.append(error)
        if errors:
            raise UserError(errors)
        # Update buffer computed fields:
        buffers = self.mapped("item_ids.buffer_id")
        buffers.invalidate_recordset()
        self.env.add_to_compute(buffers._fields["procure_recommended_qty"], buffers)
        buffers.flush_recordset()
        return {"type": "ir.actions.act_window_close"}


class MakeProcurementBufferItem(models.TransientModel):
    _name = "make.procurement.buffer.item"
    _description = "Make Procurements from Stock Buffer Item"

    wiz_id = fields.Many2one(
        comodel_name="make.procurement.buffer",
        string="Wizard",
        required=True,
        ondelete="cascade",
        readonly=True,
    )
    recommended_qty = fields.Float(readonly=True)
    qty = fields.Float()
    uom_id = fields.Many2one(
        string="Unit of Measure",
        comodel_name="uom.uom",
    )
    date_planned = fields.Datetime(string="Planned Date", required=False)
    buffer_id = fields.Many2one(
        string="Stock Buffer",
        comodel_name="stock.buffer",
        readonly=False,
    )
    product_id = fields.Many2one(
        string="Product",
        comodel_name="product.product",
        readonly=True,
    )
    warehouse_id = fields.Many2one(
        string="Warehouse",
        comodel_name="stock.warehouse",
        readonly=True,
    )
    location_id = fields.Many2one(
        string="Location",
        comodel_name="stock.location",
        readonly=True,
    )

    @api.onchange("uom_id")
    def onchange_uom_id(self):
        for rec in self:
            rec.qty = rec.buffer_id.product_uom._compute_quantity(
                rec.buffer_id.procure_recommended_qty, rec.uom_id
            )

    def _prepare_values_make_procurement(self):
        values = self.buffer_id._prepare_procurement_values(self.qty)
        values.update(
            {"date_planned": self.date_planned, "supplier_id": self.wiz_id.partner_id}
        )
        return values
