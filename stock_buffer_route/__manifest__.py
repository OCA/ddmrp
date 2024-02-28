# Copyright 2019-20 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
{
    "name": "Stock Buffer Route",
    "summary": "Allows to force a route to be used when procuring from Stock Buffers",
    "version": "14.0.1.3.0",
    "license": "LGPL-3",
    "website": "https://github.com/OCA/ddmrp",
    "author": "ForgeFlow, Camptocamp, Odoo Community Association (OCA)",
    "category": "Warehouse",
    "depends": ["ddmrp"],
    "data": [
        "views/stock_buffer_views.xml",
        "wizards/make_procurement_buffer_view.xml",
    ],
    "installable": True,
}
