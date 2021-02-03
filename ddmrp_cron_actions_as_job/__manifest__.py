# Copyright 2020 Camptocamp (https://www.camptocamp.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "DDMRP Buffer Calculation as job",
    "version": "13.0.1.1.0",
    "summary": "Run DDMRP Buffer Calculation as jobs",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/ddmrp",
    "category": "Warehouse Management",
    "depends": ["ddmrp", "queue_job"],
    "data": ["data/queue_job_channel_data.xml", "data/queue_job_function_data.xml"],
    "license": "LGPL-3",
    "installable": True,
}
