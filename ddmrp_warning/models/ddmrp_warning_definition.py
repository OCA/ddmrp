# Copyright 2021 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import _, fields, models, tools
from odoo.exceptions import UserError
from odoo.osv import expression
from odoo.tools.safe_eval import safe_eval


class DdmrpWarningDefinition(models.Model):
    _name = "ddmrp.warning.definition"
    _description = "DDMRP Warning Definition"

    name = fields.Char(
        string="Description",
    )
    python_code = fields.Text(
        string="Warning Expression",
        help="Write Python code that defines when this warning should "
        "raise. The result of executing the expression must be "
        "a boolean.",
        default="""# Available locals:\n#  - buffer: A buffer record\nTrue""",
    )
    severity = fields.Selection(
        selection=[("1_low", "Low"), ("2_mid", "Medium"), ("3_high", "High")],
        default="mid",
    )
    active = fields.Boolean(default=True)
    warning_domain = fields.Char(
        string="Buffer Applicable Domain",
        default="[]",
        help="Domain based on Stock Buffer, to define if the "
        "warning is applicable or not.",
    )

    def _eval_warning_domain(self, buffer, domain):
        buffer_domain = [("id", "=", buffer.id)]
        return bool(
            self.env["stock.buffer"].search_count(
                expression.AND([buffer_domain, domain])
            )
        )

    def _is_warning_applicable(self, buffer):
        domain = safe_eval(self.warning_domain) or []
        if domain:
            return self._eval_warning_domain(buffer, domain)
        return True

    def evaluate_definition(self, buffer):
        self.ensure_one()
        try:
            res = safe_eval(
                self.python_code,
                globals_dict={
                    "buffer": buffer,
                    "time": tools.safe_eval.time,
                    "datetime": tools.safe_eval.datetime,
                    "dateutil": tools.safe_eval.dateutil,
                },
            )
        except Exception as error:
            raise UserError(
                _("Error evaluating %(name)s.\n %(error)s")
                % ({"name": self._name, "error": error})
            ) from error
        return res
