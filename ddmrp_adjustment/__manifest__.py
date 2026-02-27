# Copyright 2017-26 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "DDMRP Adjustment",
    "summary": "Allow to apply factor adjustments to buffers.",
    "version": "18.0.2.0.0",
    "development_status": "Beta",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "maintainers": ["JordiBForgeFlow", "LoisRForgeFlow"],
    "website": "https://github.com/OCA/ddmrp",
    "category": "Warehouse",
    "depends": ["ddmrp", "date_range"],
    "data": [
        "security/ir.model.access.csv",
        "security/ddmrp_security.xml",
        "views/ddmrp_adjustment_view.xml",
        "views/ddmrp_adjustment_demand_view.xml",
        "views/stock_buffer_view.xml",
    ],
    "license": "LGPL-3",
    "installable": True,
}
