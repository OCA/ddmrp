# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
        "name": "DDMRP Exclude Moves ADU Calc",
    "summary": "Define additional rules to exclude certain moves from ADU "
               "calculation",
    "version": "9.0.1.0.0",
    "author": "Eficent,"
              "Odoo Community Association (OCA)",
    "website": "https://www.odoo-community.org",
    "category": "Warehouse Management",
    "depends": ["ddmrp"],
    "data": [
        "views/stock_move_view.xml",
        "views/stock_location_view.xml"],
    "license": "AGPL-3",
    'installable': True,
    'application': False,
}
