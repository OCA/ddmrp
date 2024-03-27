# Copyright 2023 ForgeFlow (http://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "DDMRP Exclude Location",
    "summary": "Define additional rule to exclude locations from DDMRP",
    "version": "14.0.1.0.0",
    "author": "ForgeFlow, " "Odoo Community Association (OCA)",
    "maintainers": ["BernatPForgeFlow"],
    "website": "https://github.com/OCA/ddmrp",
    "category": "Warehouse Management",
    "depends": ["ddmrp"],
    "data": ["views/stock_location_view.xml", "views/stock_buffer_view.xml"],
    "license": "LGPL-3",
    "installable": True,
    "application": False,
}
