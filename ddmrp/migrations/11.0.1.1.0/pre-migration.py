# -*- coding: utf-8 -*-
# Copyright 2018 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from psycopg2.extensions import AsIs


def migrate(cr, version):
    # pre-create columns:
    for column in ['source_past', 'source_future']:
        cr.execute("""SELECT column_name
            FROM information_schema.columns
            WHERE table_name='product_adu_calculation_method' AND
            column_name=%s""", (column,))
        if not cr.fetchone():
            cr.execute("""
                ALTER TABLE product_adu_calculation_method
                ADD COLUMN %s varchar;""", (AsIs(column),))
    for column in ['horizon_past', 'horizon_future']:
        cr.execute("""SELECT column_name
            FROM information_schema.columns
            WHERE table_name='product_adu_calculation_method' AND
            column_name=%s""", (column,))
        if not cr.fetchone():
            cr.execute("""
                ALTER TABLE product_adu_calculation_method
                ADD COLUMN %s float;""", (AsIs(column),))

    # use_estimates -> source_past and source_future:
    cr.execute("""
        UPDATE product_adu_calculation_method
        SET source_past = 'actual'
        WHERE method = 'past' AND use_estimates = false
    """)
    cr.execute("""
        UPDATE product_adu_calculation_method
        SET source_past = 'estimates'
        WHERE method = 'past' AND use_estimates = true
    """)
    cr.execute("""
        UPDATE product_adu_calculation_method
        SET source_future = 'actual'
        WHERE method = 'future' AND use_estimates = false
    """)
    cr.execute("""
        UPDATE product_adu_calculation_method
        SET source_future = 'estimates'
        WHERE method = 'future' AND use_estimates = true
    """)

    # horizon -> horizon_past and horizon_future
    cr.execute("""
        UPDATE product_adu_calculation_method
        SET horizon_past = horizon
        WHERE method = 'past'
    """)
    cr.execute("""
        UPDATE product_adu_calculation_method
        SET horizon_future = horizon
        WHERE method = 'future'
    """)
