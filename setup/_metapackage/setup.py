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
        'odoo13-addon-ddmrp_coverage_days',
        'odoo13-addon-ddmrp_history',
        'odoo13-addon-ddmrp_packaging',
        'odoo13-addon-stock_buffer_capacity_limit',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
