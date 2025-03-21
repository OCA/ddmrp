# Copyright 2017-21 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "DDMRP Product Replace",
    "summary": "Provides a assisting tool for product replacement.",
    "version": "18.0.1.0.0",
    "development_status": "Beta",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "maintainers": ["JordiBForgeFlow", "LoisRForgeFlow"],
    "website": "https://github.com/OCA/ddmrp",
    "category": "Warehouse Management",
    "depends": ["ddmrp_chatter"],
    "data": [
        "security/ir.model.access.csv",
        "wizards/ddmrp_product_replace_view.xml",
        "wizards/make_procurement_buffer_view.xml",
        "views/stock_buffer_view.xml",
    ],
    "license": "LGPL-3",
    "installable": True,
}
