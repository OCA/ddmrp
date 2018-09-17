# Copyright 2017-18 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "DDMRP Exclude Moves ADU Calc",
    "summary": "Define additional rules to exclude certain moves from ADU "
               "calculation",
    "version": "11.0.1.0.0",
    "author": "Eficent,"
              "Odoo Community Association (OCA)",
    "maintainers": ['jbeficent', 'lreficent'],
    "website": "https://github.com/OCA/ddmrp",
    "category": "Warehouse Management",
    "depends": ["ddmrp"],
    "data": [
        "views/stock_move_view.xml",
        "views/stock_location_view.xml",
    ],
    "license": "AGPL-3",
    'installable': True,
    'application': False,
}
