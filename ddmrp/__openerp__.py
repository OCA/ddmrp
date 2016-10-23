# -*- coding: utf-8 -*-
# © 2016 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# © 2016 Aleph Objects, Inc. (https://www.alephobjects.com/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "DDMRP",
    "summary": "Demand-driven MRP",
    "version": "8.0.1.0.0",
    "author": "Eficent Business and IT Consulting Services S.L,"
              "Aleph Objects, Inc.,"
              "Odoo Community Association (OCA)",
    "website": "http://www.eficent.com",
    "category": "Warehouse Management",
    "depends": ["purchase",
                "mrp",
                "web_tree_dynamic_colored_field",
                "web_widget_x2many_2d_matrix",
                "stock_warehouse_orderpoint_stock_info",
                "stock_available_unreserved"],
    "data": ["security/ir.model.access.csv",
             "security/stock_security.xml",
             "views/stock_buffer_demand_estimate_period_view.xml",
             "views/stock_buffer_demand_estimate_view.xml",
             "wizards/demand_estimate_wizard_view.xml",
             "views/stock_buffer_profile_view.xml",
             "views/product_adu_calculation_method_view.xml",
             "views/stock_warehouse_orderpoint_view.xml",
             "views/procurement_order_view.xml",
             ],
    "license": "AGPL-3",
    'installable': True,
    'application': True,
}
