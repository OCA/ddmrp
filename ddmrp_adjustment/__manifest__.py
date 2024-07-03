# Copyright 2017-23 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "DDMRP Adjustment",
    "summary": "Allow to apply factor adjustments to buffers.",
    "version": "17.0.1.0.0",
    "development_status": "Beta",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "maintainers": ["JordiBForgeFlow", "LoisRForgeFlow"],
    "website": "https://github.com/OCA/ddmrp",
    "category": "Warehouse",
    "depends": ["ddmrp", "web_widget_x2many_2d_matrix", "date_range"],
    "data": [
        "security/ir.model.access.csv",
        "security/ddmrp_security.xml",
        "views/ddmrp_adjustment_view.xml",
        "views/ddmrp_adjustment_demand_view.xml",
        "views/stock_buffer_view.xml",
        "wizards/ddmrp_adjustment_wizard_view.xml",
    ],
    "license": "AGPL-3",
    "installable": True,
}
