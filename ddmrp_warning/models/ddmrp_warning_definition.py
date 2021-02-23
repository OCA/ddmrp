# Copyright 2021 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import _, fields, models
from odoo.exceptions import UserError
from odoo.tools.safe_eval import safe_eval


class DdmrpWarningDefinition(models.Model):
    _name = "ddmrp.warning.definition"
    _description = "DDMRP Warning Definition"

    name = fields.Char(string="Description",)
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

    def evaluate_definition(self, buffer):
        self.ensure_one()
        try:
            res = safe_eval(self.python_code, globals_dict={"buffer": buffer})
        except Exception as error:
            raise UserError(_("Error evaluating %s.\n %s") % (self._name, error))
        return res
