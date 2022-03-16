# Copyright 2020 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "Stock Buffer Capacity Limit",
    "summary": "Ensures that the limits of storage are never surpassed",
    "version": "15.0.1.0.0",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "development_status": "Beta",
    "maintainers": ["LoisRForgeFlow"],
    "website": "https://github.com/OCA/ddmrp",
    "category": "Warehouse Management",
    "depends": ["ddmrp"],
    "data": ["views/stock_buffer_view.xml"],
    "license": "LGPL-3",
    "installable": True,
    "auto_install": False,
}
