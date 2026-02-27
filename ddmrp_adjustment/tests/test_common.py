# Copyright 2018 Camptocamp SA
# Copyright 2020-26 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

import datetime
from calendar import monthrange

from odoo.tests import TransactionCase
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT


class TestDDMRPAdjustmentCommon(TransactionCase):
    def _create_period(self, year, month, date_range_type):
        return self.env["date.range"].create(
            {
                "name": "%i-%i" % (year, month),
                "type_id": date_range_type.id,
                "date_start": datetime.datetime(year=year, month=month, day=1).strftime(
                    DEFAULT_SERVER_DATE_FORMAT
                ),
                "date_end": datetime.datetime(
                    year=year, month=month, day=monthrange(year, month)[1]
                ).strftime(DEFAULT_SERVER_DATE_FORMAT),
            }
        )

    def setUp(self):
        super().setUp()
        self.now = datetime.datetime.now()
        self.month_date_range_type = self.env["date.range.type"].create(
            {"name": "Month", "allow_overlap": False}
        )
        # create date ranges for each month in actual and next years
        for y in (self.now.year, self.now.year + 1):
            for m in range(1, 13):
                date_range = self._create_period(y, m, self.month_date_range_type)
                setattr(self, "month_%i_%i" % (y, m), date_range)
        self.buffer = self.env.ref("ddmrp.stock_buffer_fp01")
