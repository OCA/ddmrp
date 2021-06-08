# Copyright 2021 ForgeFlow <http://www.forgeflow.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    _logger.info("Set buffer profile data as no-update.")
    cr.execute(
        """
        UPDATE ir_model_data imd
        SET noupdate = true
        WHERE "module" = 'ddmrp' AND (
            name ILIKE 'stock_buffer_profile_replenish_%'
            OR name ILIKE 'stock_buffer_profile_min_max%'
        );
    """
    )
