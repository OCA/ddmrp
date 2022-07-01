from odoo import SUPERUSER_ID, api


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    buffers = env["stock.buffer"].search(
        [("buffer_profile_id.item_type", "=", "distributed")]
    )
    if buffers:
        buffers._calc_distributed_source_location()
