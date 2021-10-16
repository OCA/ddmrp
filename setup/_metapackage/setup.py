import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo13-addons-oca-ddmrp",
    description="Meta package for oca-ddmrp Odoo addons",
    version=version,
    install_requires=[
        'odoo13-addon-ddmrp',
        'odoo13-addon-ddmrp_adjustment',
        'odoo13-addon-ddmrp_chatter',
        'odoo13-addon-ddmrp_coverage_days',
        'odoo13-addon-ddmrp_cron_actions_as_job',
        'odoo13-addon-ddmrp_exclude_moves_adu_calc',
        'odoo13-addon-ddmrp_history',
        'odoo13-addon-ddmrp_packaging',
        'odoo13-addon-ddmrp_product_replace',
        'odoo13-addon-ddmrp_sale',
        'odoo13-addon-ddmrp_warning',
        'odoo13-addon-stock_buffer_capacity_limit',
        'odoo13-addon-stock_buffer_route',
        'odoo13-addon-stock_buffer_sales_analysis',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 13.0',
    ]
)
