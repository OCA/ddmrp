from odoo import SUPERUSER_ID, api


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    mrp_productions = env["mrp.production"].search(
        [("state", "not in", ["done", "cancel"])]
    )
    if mrp_productions:
        mrp_productions._find_buffer_link()
