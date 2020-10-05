# Copyright 2020 KMEE
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Ddmrp Simulation',
    'summary': """
        Helper to Simulate DDMRP""",
    'version': '13.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'KMEE,Odoo Community Association (OCA)',
    'website': 'https://github.com/oca/ddmrp',
    'depends': [
        'ddmrp',
        'ddmrp_history',
        'queue_job',
        'web_widget_plotly_chart',
    ],
    'data': [
        'security/ddmrp_simulation_product_result.xml',
        'security/ddmrp_simulation_total_result.xml',
        'security/ddmrp_simulation_product.xml',
        'security/ddmrp_simulation_line.xml',
        'security/ddmrp_simulation.xml',

        'data/ir_sequence.xml',

        'views/ddmrp_simulation_product_result.xml',
        'views/ddmrp_simulation_product.xml',
        'views/ddmrp_simulation_line.xml',
        'views/ddmrp_simulation.xml',
        'views/ddmrp_simulation_total_result.xml',
    ],
    'demo': [
        'demo/ddmrp_simulation_product_result.xml',
        # 'demo/ddmrp_simulation_product.xml',
        # 'demo/ddmrp_simulation_line.xml',
        # 'demo/ddmrp_simulation.xml',
    ],
    "external_dependencies": {
        "python": [
            "pandas",
            "time-machine",
        ]},
}
