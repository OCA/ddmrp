# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

{
    "name": "DDMRP Purchase Hide On-Hand Status",
    "version": "14.0.1.0.0",
    "summary": "Replace purchase onhand status with smart button.",
    "author": "Camptocamp SA, Odoo Community Association (OCA)",
    "development_status": "Beta",
    "maintainers": ["TDu"],
    "website": "https://github.com/OCA/ddmrp",
    "category": "Warehouse Management",
    "depends": ["ddmrp"],
    "data": [
        "views/purchase_order_view.xml",
    ],
    "license": "LGPL-3",
    "installable": True,
}
