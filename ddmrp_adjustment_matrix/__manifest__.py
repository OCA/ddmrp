# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "DDMRP Adjustment Matrix",
    "summary": "Wizard to manage DDMRP Adjustments with a 2D matrix.",
    "version": "18.0.1.0.0",
    "development_status": "Beta",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "maintainers": ["JordiBForgeFlow", "LoisRForgeFlow"],
    "website": "https://github.com/OCA/ddmrp",
    "category": "Warehouse",
    "depends": ["ddmrp_adjustment", "web_widget_x2many_2d_matrix"],
    "data": [
        "security/ir.model.access.csv",
        "wizards/ddmrp_adjustment_wizard_view.xml",
    ],
    "license": "AGPL-3",
    "installable": True,
    "auto_install": True,
}
