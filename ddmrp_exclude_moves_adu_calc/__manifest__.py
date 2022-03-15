# Copyright 2017-21 ForgeFlow (http://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "DDMRP Exclude Moves ADU Calc",
    "summary": "Define additional rules to exclude certain moves from ADU "
    "calculation",
    "version": "15.0.1.0.0",
    "author": "ForgeFlow, " "Odoo Community Association (OCA)",
    "maintainers": ["JordiBForgeFlow", "LoisRForgeFlow"],
    "website": "https://github.com/OCA/ddmrp",
    "category": "Warehouse Management",
    "depends": ["ddmrp"],
    "data": ["views/stock_move_view.xml", "views/stock_location_view.xml"],
    "license": "LGPL-3",
    "installable": True,
    "application": False,
}
