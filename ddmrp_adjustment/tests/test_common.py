# Copyright 2018 Camptocamp SA
# Copyright 2020-26 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

import datetime
from calendar import monthrange

from odoo.tools import DEFAULT_SERVER_DATE_FORMAT

from odoo.addons.ddmrp.tests.common import TestDdmrpCommon


class TestDDMRPAdjustmentCommon(TestDdmrpCommon):
    @classmethod
    def _create_period(cls, year, month, date_range_type):
        return cls.env["date.range"].create(
            {
                "name": f"{year}-{month}",
                "type_id": date_range_type.id,
                "date_start": datetime.datetime(year=year, month=month, day=1).strftime(
                    DEFAULT_SERVER_DATE_FORMAT
                ),
                "date_end": datetime.datetime(
                    year=year, month=month, day=monthrange(year, month)[1]
                ).strftime(DEFAULT_SERVER_DATE_FORMAT),
            }
        )

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.now = datetime.datetime.now()
        cls.month_date_range_type = cls.env["date.range.type"].create(
            {"name": "Month", "allow_overlap": False}
        )
        # create date ranges for each month in actual and next years
        for y in (cls.now.year, cls.now.year + 1):
            for m in range(1, 13):
                date_range = cls._create_period(y, m, cls.month_date_range_type)
                setattr(cls, f"month_{y}_{m}", date_range)
        cls.buffer = cls.buffer_fp01
