import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo14-addons-oca-ddmrp",
    description="Meta package for oca-ddmrp Odoo addons",
    version=version,
    install_requires=[
        'odoo14-addon-ddmrp',
        'odoo14-addon-ddmrp_adjustment',
        'odoo14-addon-ddmrp_chatter',
        'odoo14-addon-ddmrp_coverage_days',
        'odoo14-addon-ddmrp_cron_actions_as_job',
        'odoo14-addon-ddmrp_exclude_moves_adu_calc',
        'odoo14-addon-ddmrp_history',
        'odoo14-addon-ddmrp_packaging',
        'odoo14-addon-ddmrp_product_replace',
        'odoo14-addon-ddmrp_warning',
        'odoo14-addon-stock_buffer_capacity_limit',
        'odoo14-addon-stock_buffer_route',
        'odoo14-addon-stock_buffer_sales_analysis',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
