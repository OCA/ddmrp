# Copyright 2017-20 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "DDMRP History",
    "summary": "Allow to store historical data of DDMRP buffers.",
    "version": "13.0.1.3.1",
    "development_status": "Beta",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "maintainers": ["JordiBForgeFlow", "LoisRForgeFlow"],
    "website": "https://github.com/OCA/ddmrp",
    "category": "Warehouse Management",
    "depends": ["ddmrp"],
    "data": [
        "security/ir.model.access.csv",
        "views/ddmrp_history_view.xml",
        "views/stock_buffer_view.xml",
    ],
    "demo": ["demo/ddmrp.history.csv"],
    "external_dependencies": {"python": ["pandas"]},
    "license": "LGPL-3",
    "installable": True,
}
