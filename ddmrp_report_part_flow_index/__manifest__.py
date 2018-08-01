# Copyright 2017-18 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "DDMRP Report Part Flow Index",
    "summary": "Provides the DDMRP Parts Flow Index Report",
    "version": "11.0.1.0.0",
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
        "reports/report_ddmrp_part_plan_flow_index_views.xml",
        "views/ddmrp_flow_index_group_views.xml",
        "views/stock_warehouse_orderpoint_view.xml",
    ],
    "license": "AGPL-3",
    'installable': True,
}
