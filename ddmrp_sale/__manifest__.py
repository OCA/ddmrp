# Copyright 2021 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "DDMRP Sale",
    "summary": "DDMRP integration with Sales app.",
    "version": "13.0.1.0.0",
    "development_status": "Beta",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "maintainers": ["LoisRForgeFlow"],
    "website": "https://github.com/OCA/ddmrp",
    "category": "Warehouse Management",
    "depends": ["ddmrp", "sale_order_line_date"],
    "data": ["views/stock_buffer_view.xml"],
    "license": "LGPL-3",
    "installable": True,
}
