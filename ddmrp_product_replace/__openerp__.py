# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "DDMRP Product Replace",
    "summary": "Provides a assisting tool for product replacement.",
    "version": "9.0.1.0.0",
    "author": "Eficent",
    "website": "http://www.eficent.com",
    "category": "Warehouse Management",
    "depends": [
        "ddmrp",
        "stock_putaway_product",
    ],
    "data": [
        "wizards/ddmrp_product_replace_view.xml",
    ],
    "license": "AGPL-3",
    'installable': True,
}
