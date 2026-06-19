# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)


from odoo import models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def action_ddmrp_line_details(self):
        action = self.env["ir.actions.actions"]._for_xml_id(
            "ddmrp.po_line_execution_action"
        )
        action["domain"] = [("id", "in", self.order_line.ids)]
        return action
