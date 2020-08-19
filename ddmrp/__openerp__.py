# -*- coding: utf-8 -*-
# © 2016 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# © 2016 Aleph Objects, Inc. (https://www.alephobjects.com/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "DDMRP",
    "summary": "Demand Driven Material Requirements Planning",
    "version": "9.0.2.1.0",
    "author": "Eficent,"
              "Aleph Objects, Inc.,"
              "Odoo Community Association (OCA)",
    "website": "http://www.eficent.com",
    "category": "Warehouse Management",
    "depends": ["purchase",
                "mrp_bom_location",
                "web_tree_dynamic_colored_field",
                "stock_warehouse_orderpoint_stock_info",
                "stock_warehouse_orderpoint_stock_info_unreserved",
                "stock_available_unreserved",
                "stock_orderpoint_uom",
                "stock_orderpoint_manual_procurement",
                "stock_demand_estimate",
                "web_widget_bokeh_chart",
                "mrp_mto_with_stock",
                "base_cron_exclusion",
                "web_tree_many2one_clickable",
                ],
    "data": ["data/product_adu_calculation_method_data.xml",
             "data/stock_buffer_profile_variability_data.xml",
             "data/stock_buffer_profile_lead_time_data.xml",
             "data/stock_buffer_profile_data.xml",
             "security/ir.model.access.csv",
             "security/stock_security.xml",
             "views/stock_buffer_profile_view.xml",
             "views/stock_buffer_profile_variability_view.xml",
             "views/stock_buffer_profile_lead_time_view.xml",
             "views/product_adu_calculation_method_view.xml",
             "views/stock_warehouse_orderpoint_view.xml",
             "views/procurement_order_view.xml",
             "views/mrp_production_view.xml",
             "views/purchase_order_line_view.xml",
             "views/mrp_bom_view.xml",
             "views/report_mrpbomstructure.xml",
             "data/ir_cron.xml",
             ],
    "demo": [
        "demo/res_partner_demo.xml",
        "demo/product_category_demo.xml",
        "demo/product_product_demo.xml",
        "demo/product_supplierinfo_demo.xml",
        "demo/mrp_bom_demo.xml",
        "demo/stock_warehouse_orderpoint_demo.xml",
    ],
    "license": "AGPL-3",
    'installable': True,
    'application': True,
}
