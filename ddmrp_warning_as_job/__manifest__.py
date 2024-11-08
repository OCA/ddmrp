# Copyright 2024 ForgeFlow (https://www.camptocamp.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "DDMRP Warning as job",
    "version": "17.0.1.0.0",
    "summary": "Run DDMRP Warning as jobs",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/ddmrp",
    "category": "Warehouse Management",
    "depends": ["ddmrp_warning", "ddmrp_cron_actions_as_job", "queue_job"],
    "data": ["data/queue_job_function_data.xml"],
    "license": "LGPL-3",
    "installable": True,
}
