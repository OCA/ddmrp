# Copyright 2017 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "DDMRP Adjustment",
    "summary": "Allow to apply factor adjustments to buffers.",
    "version": "11.0.1.1.0",
    "development_status": "Beta",
    "author": "Eficent, Odoo Community Association (OCA)",
    "maintainers": ['jbeficent', 'lreficent'],
    "website": "https://github.com/OCA/ddmrp",
    "category": "Warehouse Management",
    "depends": [
        "ddmrp",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/ddmrp_adjustment_view.xml",
        "views/ddmrp_adjustment_demand_view.xml",
        "views/stock_warehouse_orderpoint.xml",
        "wizards/ddmrp_adjustment_wizard_view.xml",
    ],
    "license": "AGPL-3",
    'installable': True,
}
