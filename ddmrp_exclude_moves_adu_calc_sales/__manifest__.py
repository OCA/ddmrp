# Copyright 2024 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "DDMRP Exclude Moves ADU Calc Sales",
    "summary": "DDMRP Exclude Moves ADU Calc integration with Sales app.",
    "version": "18.0.2.0.0",
    "development_status": "Beta",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "maintainers": ["DavidJForgeFlow"],
    "website": "https://github.com/OCA/ddmrp",
    "category": "Warehouse Management",
    "depends": ["sale", "ddmrp_exclude_moves_adu_calc"],
    "data": ["views/sale_order_view.xml"],
    "license": "LGPL-3",
    "installable": True,
}
