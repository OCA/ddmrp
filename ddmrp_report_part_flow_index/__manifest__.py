# Copyright 2017-24 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "DDMRP Report Part Flow Index",
    "summary": "Provides the DDMRP Parts Flow Index Report",
    "version": "16.0.1.2.0",
    "development_status": "Beta",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "maintainers": ["JordiBForgeFlow", "LoisRForgeFlow"],
    "website": "https://github.com/OCA/ddmrp",
    "category": "Warehouse Management",
    "depends": [
        "ddmrp",
    ],
    "data": [
        "security/ir.model.access.csv",
        "security/report_ddmrp_part_plan_flow_index_security.xml",
        "reports/report_ddmrp_part_plan_flow_index_views.xml",
        "views/ddmrp_flow_index_group_views.xml",
        "views/stock_buffer_view.xml",
    ],
    "license": "LGPL-3",
    "installable": True,
}
