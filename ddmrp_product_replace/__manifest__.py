# Copyright 2017-18 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "DDMRP Product Replace",
    "summary": "Provides a assisting tool for product replacement.",
    "version": "11.0.1.0.1",
    "development_status": "Beta",
    "author": "Eficent, Odoo Community Association (OCA)",
    "maintainers": ['jbeficent', 'lreficent'],
    "website": "https://github.com/OCA/ddmrp",
    "category": "Warehouse Management",
    "depends": [
        "ddmrp",
        "stock_putaway_product",
    ],
    "data": [
        "wizards/ddmrp_product_replace_view.xml",
        "views/stock_warehouse_orderpoint_view.xml",
    ],
    "license": "AGPL-3",
    'installable': True,
}
