# -*- coding: utf-8 -*-
# Copyright 2019 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


def migrate(cr, version):
    cr.execute("""
        UPDATE ddmrp_adjustment
        SET adjustment_type = 'DAF', value = daf
        WHERE daf > 0.0
    """)
    cr.execute("""
        UPDATE ddmrp_adjustment
        SET adjustment_type = 'LTAF',  value = ltaf
        WHERE ltaf > 0.0
    """)
