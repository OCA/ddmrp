# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "DDMRP History",
    "summary": "Allow to store historical data of DDMRP buffers.",
    "version": "9.0.1.0.0",
    "author": "Eficent",
    "website": "http://www.eficent.com",
    "category": "Warehouse Management",
    "depends": ["ddmrp"],
    "data": [
        "security/ir.model.access.csv",
        "views/ddmrp_history_view.xml",
        "views/stock_warehouse_orderpoint_view.xml",
    ],
    "license": "AGPL-3",
    'installable': True,
}
