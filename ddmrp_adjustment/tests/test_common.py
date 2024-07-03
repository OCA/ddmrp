# Copyright 2018 Camptocamp SA
# Copyright 2020 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import datetime
from calendar import monthrange

from dateutil.relativedelta import relativedelta

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

    def _create_adjustment_wizard(self, number_of_periods):
        date_start = datetime.datetime(year=self.now.year, month=self.now.month, day=1)
        date_end = (
            date_start + relativedelta(months=number_of_periods) - relativedelta(days=1)
        )
        wiz = self.env["ddmrp.adjustment.sheet"].create(
            {
                "date_start": date_start.strftime(DEFAULT_SERVER_DATE_FORMAT),
                "date_end": date_end.strftime(DEFAULT_SERVER_DATE_FORMAT),
                "date_range_type_id": self.month_date_range_type.id,
            }
        )
        wiz.buffer_ids = [(4, self.buffer.id, False)]
        wiz.action_refresh()
        return wiz

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
