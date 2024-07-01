# Copyright 2021 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "DDMRP Warning",
    "version": "17.0.1.0.0",
    "summary": "Adds configuration warnings on stock buffers.",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "development_status": "Production/Stable",
    "maintainers": ["LoisRForgeFlow"],
    "website": "https://github.com/OCA/ddmrp",
    "category": "Warehouse Management",
    "depends": ["ddmrp"],
    "data": [
        "security/ir.model.access.csv",
        "security/ddmrp_warning_rules.xml",
        "views/ddmrp_buffer_view.xml",
        "views/ddmrp_warning_definition_views.xml",
        "views/ddmrp_warning_item_views.xml",
        "data/ir_cron.xml",
        "data/ddmrp_warning_definition_data.xml",
    ],
    "license": "LGPL-3",
    "installable": True,
}
