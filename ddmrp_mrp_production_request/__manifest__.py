# -*- coding: utf-8 -*-
# Copyright 2017-18 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "DDMRP Manufacturing Request",
    "summary": "Allows to prioritize Manufacturing Requests in a DDMRP "
               "strategy.",
    "version": "10.0.1.0.0",
    "category": "Manufacturing",
    "website": "https://github.com/OCA/manufacture",
    "author": "Eficent, "
              "Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": False,
    "auto_install": True,
    "depends": ["mrp_production_request", "ddmrp"],
    "data": [
        "views/mrp_production_request_view.xml",
    ],
}
