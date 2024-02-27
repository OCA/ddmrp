import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo-addons-oca-ddmrp",
    description="Meta package for oca-ddmrp Odoo addons",
    version=version,
    install_requires=[
        'odoo-addon-ddmrp>=16.0dev,<16.1dev',
        'odoo-addon-ddmrp_adjustment>=16.0dev,<16.1dev',
        'odoo-addon-ddmrp_chatter>=16.0dev,<16.1dev',
        'odoo-addon-ddmrp_exclude_moves_adu_calc>=16.0dev,<16.1dev',
        'odoo-addon-ddmrp_exclude_moves_adu_calc_sales>=16.0dev,<16.1dev',
        'odoo-addon-ddmrp_history>=16.0dev,<16.1dev',
        'odoo-addon-ddmrp_product_replace>=16.0dev,<16.1dev',
        'odoo-addon-ddmrp_sale>=16.0dev,<16.1dev',
        'odoo-addon-ddmrp_warning>=16.0dev,<16.1dev',
        'odoo-addon-stock_buffer_route>=16.0dev,<16.1dev',
        'odoo-addon-stock_buffer_sales_analysis>=16.0dev,<16.1dev',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 16.0',
    ]
)
