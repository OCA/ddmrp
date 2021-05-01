# Copyright 2020 KMEE
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Ddmrp Simulation Remote',
    'summary': """
        Connect to other Odoo to get DDMRP simulation data""",
    'version': '13.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'KMEE,Odoo Community Association (OCA)',
    'website': 'https://github.com/oca/ddmrp',
    'depends': [
        'ddmrp_simulation',
    ],
    'data': [
    ],
    'demo': [
    ],
    "external_dependencies": {
        "python": [
            "odoorpc",
        ]},
}
