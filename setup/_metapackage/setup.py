import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo11-addons-oca-ddmrp",
    description="Meta package for oca-ddmrp Odoo addons",
    version=version,
    install_requires=[
        'odoo11-addon-ddmrp_production_equivalent',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
