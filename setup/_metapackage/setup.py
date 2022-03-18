import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo-addons-oca-ddmrp",
    description="Meta package for oca-ddmrp Odoo addons",
    version=version,
    install_requires=[
        'odoo-addon-ddmrp>=15.0dev,<15.1dev',
        'odoo-addon-ddmrp_adjustment>=15.0dev,<15.1dev',
        'odoo-addon-ddmrp_chatter>=15.0dev,<15.1dev',
        'odoo-addon-ddmrp_coverage_days>=15.0dev,<15.1dev',
        'odoo-addon-ddmrp_cron_actions_as_job>=15.0dev,<15.1dev',
        'odoo-addon-ddmrp_exclude_moves_adu_calc>=15.0dev,<15.1dev',
        'odoo-addon-ddmrp_history>=15.0dev,<15.1dev',
        'odoo-addon-ddmrp_warning>=15.0dev,<15.1dev',
        'odoo-addon-stock_buffer_capacity_limit>=15.0dev,<15.1dev',
        'odoo-addon-stock_buffer_route>=15.0dev,<15.1dev',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 15.0',
    ]
)
